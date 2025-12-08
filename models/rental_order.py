from odoo import models, fields, api, Command
from odoo.exceptions import UserError

class RentalOrder(models.Model):
    _name = 'rental.order'
    _description = 'Rental Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_order desc'
    _check_company_auto = True

    name = fields.Char(
        string='Order Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('rental.order') or 'New'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        check_company=True
    )
    
    date_order = fields.Datetime(
        string='Order Date',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    
    date_start = fields.Date(
        string='Start Date',
        required=True,
        tracking=True
    )
    
    date_end = fields.Date(
        string='End Date',
        required=True,
        tracking=True
    )
    
    rental_duration = fields.Integer(
        string='Duration (Days)',
        compute='_compute_rental_duration',
        store=True,
        readonly=True
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Rental Product',
        required=True,
        domain=[('detailed_type', '=', 'service')],
        check_company=True
    )
    
    price_unit = fields.Float(
        string='Daily Rate',
        required=True,
        digits='Product Price'
    )
    
    price_total = fields.Monetary(
        string='Total Price',
        compute='_compute_price_total',
        store=True,
        tracking=True,
        currency_field='currency_id'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True, copy=False)
    
    invoice_ids = fields.One2many(
        'account.move',
        'rental_order_id',
        string='Invoices',
        readonly=True
    )
    
    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_compute_invoice_count',
        compute_sudo=True
    )
    
    invoice_status = fields.Selection([
        ('no', 'Nothing to Invoice'),
        ('to_invoice', 'To Invoice'),
        ('invoiced', 'Fully Invoiced')
    ], string='Invoice Status', compute='_compute_invoice_status', store=True)
    
    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
        tracking=True,
        check_company=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True
    )
    
    notes = fields.Html(string='Notes')
    
    @api.depends('date_start', 'date_end')
    def _compute_rental_duration(self):
        for record in self:
            if record.date_start and record.date_end:
                delta = record.date_end - record.date_start
                record.rental_duration = max(delta.days + 1, 0)
            else:
                record.rental_duration = 0
    
    @api.depends('price_unit', 'rental_duration')
    def _compute_price_total(self):
        for record in self:
            record.price_total = record.price_unit * record.rental_duration
    
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)
    
    @api.depends('invoice_ids', 'invoice_ids.state', 'state')
    def _compute_invoice_status(self):
        for record in self:
            if record.state in ['draft', 'cancelled']:
                record.invoice_status = 'no'
            elif not record.invoice_ids:
                record.invoice_status = 'to_invoice' if record.state in ['confirmed', 'in_progress', 'done'] else 'no'
            elif all(inv.payment_state in ['paid', 'in_payment'] for inv in record.invoice_ids.filtered(lambda m: m.state == 'posted')):
                record.invoice_status = 'invoiced'
            else:
                record.invoice_status = 'to_invoice'
    
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end and record.date_end < record.date_start:
                raise UserError('End date must be after or equal to start date!')
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
        return True
    
    def action_start(self):
        for record in self:
            record.state = 'in_progress'
        return True
    
    def action_done(self):
        for record in self:
            record.state = 'done'
        return True
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
        return True
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'
        return True
    
    def action_create_invoice(self):
        self.ensure_one()
        
        if not self.partner_id:
            raise UserError('Please select a customer before creating an invoice.')
        
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.context_today(self),
            'rental_order_id': self.id,
            'company_id': self.company_id.id,
            'invoice_line_ids': [
                Command.create({
                    'product_id': self.product_id.id,
                    'name': f'Rental: {self.product_id.name} ({self.date_start} to {self.date_end})',
                    'quantity': self.rental_duration,
                    'price_unit': self.price_unit,
                })
            ],
        }
        
        invoice = self.env['account.move'].sudo().create(invoice_vals)
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Invoice',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'current',
        }
    
    def action_view_invoices(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'context': {
                'default_rental_order_id': self.id,
                'default_move_type': 'out_invoice',
            },
            'view_mode': 'tree,form',
        }
        
        if len(self.invoice_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.invoice_ids.id,
                'views': [(False, 'form')],
            })
        
        return action


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    rental_order_id = fields.Many2one(
        'rental.order',
        string='Rental Order',
        readonly=True,
        copy=False
    )