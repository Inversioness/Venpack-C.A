# -*- coding: utf-8 -*-
{
    'name': "entry report",

    'summary': "entry report",

    'description': """
    entry report
    """,

    'author': "Arkisoft / nikolays Toro",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'studio_customization'], 

    # always loaded
    'data': [
        'views/reporte_asiento.xml',
    ]
}

