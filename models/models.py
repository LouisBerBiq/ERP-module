from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_bike = fields.Boolean(string="Est un vélo de location")
    rent_price_day = fields.Float(string="Prix location / jour")

class BikeRental(models.Model):
    _name = 'bike.rental'
    _description = 'Contrat de Location'

    name = fields.Char(string="Référence", required=True, copy=False, readonly=True, default='Nouveau')
    partner_id = fields.Many2one('res.partner', string="Client", required=True)
    bike_id = fields.Many2one('product.product', string="Vélo", required=True, domain="[('is_bike', '=', True)]")
    start_date = fields.Date(string="Date début", default=fields.Date.today, required=True)
    end_date = fields.Date(string="Date fin", required=True)
    return_date = fields.Date(string="Date retour réelle", readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'), ('in_progress', 'Loué'),
        ('overdue', 'En retard'), ('done', 'Terminé'), 
    ], default='draft', string="État")
    total_price = fields.Float(string="Prix Total", compute='_compute_total_price', store=True)
    days_overdue = fields.Integer(string="Jours en retard", compute='_compute_days_overdue', store=True)

    @api.depends('start_date', 'end_date', 'bike_id.rent_price_day')
    def _compute_total_price(self):
        for record in self:
            if record.start_date and record.end_date and record.bike_id:
                days = (record.end_date - record.start_date).days + 1
                record.total_price = days * record.bike_id.rent_price_day if days > 0 else 0
            else:
                record.total_price = 0

    @api.depends('end_date', 'return_date', 'state')
    def _compute_days_overdue(self):
        today = fields.Date.today()
        for record in self:
            if record.state in ['in_progress', 'overdue']:
                check_date = record.return_date or today
                days = (check_date - record.end_date).days
                record.days_overdue = max(days, 0)
            else:
                record.days_overdue = 0

    def action_confirm(self):
        self.state = 'in_progress'
        if self.name == 'Nouveau':
            self.name = self.env['ir.sequence'].next_by_code('bike.rental') or 'LOC'
    
    def action_done(self):
        self.return_date = fields.Date.today()
        # Compute days overdue locally to avoid timing issues with computed fields
        days_overdue = (self.return_date - self.end_date).days
        if days_overdue > 0:
            self.state = 'overdue'
        else:
            self.state = 'done'