{
    'name'    : 'Alternative Production Products',

    'summary' : """Replace products without stock with alternative ones on mrp productions""",
    'author'  : 'ARXI',
    'website' : 'https://www.arxi.pt',
    'category': 'Manufacturing/Manufacturing',
    'version' : '15.0.0.0.0',
    'price'   : 54.00,
    'currency': 'EUR',

    'license' : 'OPL-1',
    'depends' : ['mrp'],
    'data'    : [
        'security/ir.model.access.csv',
        'views/product_views.xml'
    ],
    'images'  : ['static/description/banner.gif'],
}
