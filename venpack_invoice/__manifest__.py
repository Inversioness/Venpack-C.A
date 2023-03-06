# -*- coding: utf-8 -*-
{
    'name': "Venpack Invoice",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Fabio Tamburini",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock', 'tax_report'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/paper_format.xml',
        'views/account_move.xml',
        # 'views/sale_order.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
        'views/venpack_report.xml',
        'reports/venpack_invoice.xml',
        'reports/second_venpack_invoice.xml',
        'reports/third_venpack_invoice.xml',
        'reports/fourth_venpack_invoice.xml',
        'reports/tracking_guide.xml',
        'reports/municipal_taxes.xml',
        'reports/financial_budget.xml',
        'reports/municipal_withholding_list.xml',
        'reports/municipal_withholding.xml',
        'wizard/report_municipal_withholding.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
