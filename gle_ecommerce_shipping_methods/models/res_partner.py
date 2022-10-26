from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    shipping_methods = fields.Many2many('delivery.carrier', string='Delivery Methods')
