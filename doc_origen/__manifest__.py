# -*- coding: utf-8 -*-
{
    'name': 'Apuntes Origen',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'author': "Arkisoft / Nikolays Toro",
    'website': "https://www.yourcompany.com",
    'summary': 'Duplica la vista de asientos contables con un nuevo acceso de menú.',
    'depends': [
        'account',
        'stock_account',
    ],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}