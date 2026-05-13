# -*- coding: utf-8 -*-
{
    'name': "Valuation modificaction",

    'summary': "Valuation modificaction",

    'description': """
Valuation modificaction 
    """,

    'author': "Arkisoft / Nikolays Toro",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.0.5',

    'depends': ['base', 'account', 'stock', 'purchase', 'stock_account'],

    # always loaded 
    'data': [
        'views/stock_valuation.xml',
        'views/product_view.xml',
    ],
    'installable': True,
}

