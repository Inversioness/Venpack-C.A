# -*- coding: utf-8 -*-
# Copyright (C) 2021-Today: Part of NextFlowIT.
# @author:  Part of NextFlowIT.

{
    'name': "Point of Sale Discounted Price",
    'summary': """Point of Sale Discounted Price pos Price show and actual price in pos show discount in pos price in pos pricelist price display pos order discounte discount per product base discount display line discount display in show price price discounte show price in receipt show price line price discounted pricelist pricelist detail pricelist pricelist price pos display price pos display pricelist pos display pos receipt pos discount pos discounted""",
    'author': 'NextFlowIT',
    "license": "OPL-1",
    'description': """  This module is help you to display product actual price and discounted price in pos Point of Sale Discounted Price show discount in pos , """,
    'category': "Point of sale",
    'website': '',
    'depends': ['point_of_sale'],
    'version': '16.0.3',
    'data': ['views/nf_pos_config_view.xml', ],
    'assets': {
        'point_of_sale.assets': [
            'nf_pos_discounted_product/static/src/js/nf_pos_custom.js',
            'nf_pos_discounted_product/static/src/scss/nf_pos_custom_css.css',
            'nf_pos_discounted_product/static/src/xml/nf_pos_config.xml',
        ],
    },
    "images": ["static/description/background.png", ],
    "price": 20,
    'installable': True,
    'application': True,
    'auto_install': False,
    "currency": "EUR"
}
