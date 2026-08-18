# -*- coding: utf-8 -*-
{
    'name': "reverse_rate",

    'summary': "reverse rate",

    'description': """
    validacion para tasa inversa
    """,

    'author': "Arkisoft / Nikolays Toro",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.0.5',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'stock', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'view/tasa.xml',
    ]
}

