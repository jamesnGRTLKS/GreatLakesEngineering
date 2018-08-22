# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'eCommerce Access Customization',
    'description': """
    - eCommerce Access Customization
    - Set customers on product
    """,
    'category': 'Website',
    'depends': ['website_sale'],
    'data': [
        'views/product_view.xml',
        ],
    'license': 'OEEL-1',
    'installable': True,
}
