# -*- coding: utf-8 -*-
{
    'name': "Venpack Invoice",

    'summary': """
        Personalized invoices for venpack""",

    'description': """
        Personalized invoices for venpack
    """,

    'author': "Arkisoft / Fabio Tamburini",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing',
    'version': '16.0.1',

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
        'reports/financial_budget_v2.xml',
        'reports/municipal_withholding_list.xml',
        'reports/municipal_withholding.xml',
        'wizard/report_municipal_withholding.xml',
    ],

    # 'assets': {
    #     'web.assets_backend': [
    #         'venpack_invoice/static/src/css/custom_css_reports.css'
    #     ],
    # }
}
