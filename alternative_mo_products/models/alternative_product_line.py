from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AlternativeProductLine(models.Model):
    _name = 'alternative.product.line'
    _description = "Alternative Product Line"
    _order = 'sequence'

    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product')
    alternative_product_id = fields.Many2one('product.product', required=True)
    ratio = fields.Float(default=1)

    @api.constrains('product_id', 'alternative_product_id')
    def _check_alternative_product_id(self):
        for rec in self:
            if rec.alternative_product_id and rec.product_id == rec.alternative_product_id:
                raise ValidationError(_('A product cannot be an alternative to it self!'))

    @api.onchange('alternative_product_id')
    def onchange_product_uom_id(self):
        res = {}
        if not self.alternative_product_id:
            return
        if self.alternative_product_id.uom_id.category_id.id != self.product_id.uom_id.category_id.id:
            self.alternative_product_id = False
            res['warning'] = {'title'  : _('Warning'), 'message': _(
                'The Product you chose has a different unit of measure category than the original product.')}
        return res

