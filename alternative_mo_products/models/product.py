from odoo import  fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    alternative_line_ids = fields.One2many('alternative.product.line', 'product_id',
                                           string='Alternative Products (production)', copy=True, auto_join=True)
