# -*- coding: utf-8 -*-
{
    'name': "tax_report",

    'summary': """
        Collection of tax reports""",

    'description': """
        Collection of tax reports
    """,

    'author': "Fabio Tamburini",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'web_domain_field', 'bi_manual_currency_exchange_rate', "report_xlsx"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/paper_format.xml',
        'views/actions_report.xml',
        'views/res_partner.xml',
        'views/account_move.xml',
        'views/sales_purchase_book.xml',
        'views/iva_txt.xml',
        'views/res_company_views.xml',
        'views/account_journal_views.xml',
        # 'views/report_templates.xml', #TODO utilizado para modificar el reporte de modelo de conciliacion
        # 'views/res_config_settings.xml',
        'wizard/account_payment_register_views.xml',
        'wizard/report_islr_xml.xml',
        'reports/islr_voucher.xml',
        'reports/iva_voucher.xml',
        'reports/iva_txt.xml',
        'reports/sales_book.xml',
        'reports/purchase_book.xml',
        'reports/financial_summary.xml',
        'reports/islr_listing.xml',
        'reports/iva_listing.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'assets': {
        'web.assets_qweb': [
            'tax_report/static/src/xml/**/*',
        ],
    },
}
