# -*- coding: utf-8 -*-
{
    'name': "Purchase Line",

    'summary': "Purchase Line",

    'description': """
Purchase Line MAH
    """,

    'author': "Arkisoft / Nikolays Toro",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.0.5',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'stock', 'web'],

    # always loaded 
    'data': [
        'security/ir.model.access.csv',
        'data/purchase_lines_report_column.xml',
        #boton menu 
        'views/ir_action.xml',
        'wizards/report_purchase_line_wizard_view.xml',
        
        #botonces imprimir
        'reports/server_actions.xml',
        #'reports/report_purchase_line_template.xml',
    ]
}

