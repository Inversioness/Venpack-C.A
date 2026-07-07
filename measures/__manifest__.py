# -*- coding: utf-8 -*-
{
    'name': "purchasing measures",

    'summary': "purchasing measures",

    'description': """
measures
    """,

    'author': "Arkisoft / Nikolays Toro",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.0.5',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'product'],

    # always loaded 
    'data': [
        'views/purchase_order_view.xml',
        'views/purchase_reports.xml',
        'views/sale_reports.xml',
    ]
}

