# -*- coding: utf-8 -*-
{
    'name': "Tax Report Customization",

    'summary': """
        Customization of tax reports""",

    'description': """
        Customization of tax reports
    """,

    'author': "Fabio Tamburini",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'tax_report'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/blank_tax_report_wizard.xml',
    ],
}
