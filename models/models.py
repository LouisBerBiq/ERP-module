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
    state = fields.Selection([
        ('draft', 'Brouillon'), ('confirm', 'Confirmé'),
        ('done', 'Terminé'), ('cancel', 'Annulé'),
    ], default='draft', string="État")
    total_price = fields.Float(string="Prix Total", compute='_compute_total_price', store=True)

    @api.depends('start_date', 'end_date', 'bike_id.rent_price_day')
    def _compute_total_price(self):
        for record in self:
            if record.start_date and record.end_date and record.bike_id:
                days = (record.end_date - record.start_date).days + 1
                record.total_price = days * record.bike_id.rent_price_day if days > 0 else 0
            else:
                record.total_price = 0

    def action_confirm(self):
        self.state = 'confirm'
        if self.name == 'Nouveau':
            self.name = self.env['ir.sequence'].next_by_code('bike.rental') or 'LOC'
    
    def action_done(self):
        self.state = 'done'