
{
    "name": """Venezuela: POS show dual currency""",
    "summary": """Adds price  of other currency at products in POS""",
    "category": "Point Of Sale",
    "version": "16.0.1.2.0",
    "application": False,
    'author': 'José Luis Vizcaya López',
    'company': 'José Luis Vizcaya López',
    'maintainer': 'José Luis Vizcaya López',
    'website': 'https://github.com/birkot',
    "depends": ["point_of_sale", "stock"],
    "data": [
        "views/pos_payment_method.xml",
        "views/pos_session.xml",
        "views/pos_payment.xml",
        "views/pos_config.xml",
        "views/res_config_settings.xml",
        'views/pos_order.xml',
        'views/report_saledetails.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'pos_show_dual_currency/static/src/css/pos.css',
            'pos_show_dual_currency/static/src/js/**/*',
            'pos_show_dual_currency/static/src/xml/**/*.xml',
        ],
    },
    "license": "OPL-1",
    'images': [
        'static/description/thumbnail.png',
    ],
    "price": 100,
    "currency": "USD",
    "auto_install": False,
    "installable": True,
}
