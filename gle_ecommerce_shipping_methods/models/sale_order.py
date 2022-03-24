# -*- coding: utf-8 -*-
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_delivery_methods(self):
        # Lists shipping methods which belong to client and those which are published on website
        # (this method overwrites the original one)
        return self.env['delivery.carrier'].sudo().search(
            [('website_published', '=', True), ('id', 'in', self.partner_id.shipping_methods.ids)])
