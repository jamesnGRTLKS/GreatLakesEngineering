# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    customer_ids = fields.Many2many('res.partner', string="Customers")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        user = self.env.user
        '''
            check if the user signed in is a portal user or there is no user signd in and then reutnr products according to the logic below:
            1. No user signed: Only global products (no customer set on product)
            2. User signed in: Global products + Products where the user is tagged in
        '''
        if user.has_group('base.group_portal') or user.has_group('base.group_public'):
            partner = user.partner_id
            partners = [partner.id, partner.parent_id.id]
            args = args + ['|', ('customer_ids', '=', False), ('customer_ids', 'in', partners)]
        return super(ProductTemplate, self).search(args, offset, limit, order, count=count)
