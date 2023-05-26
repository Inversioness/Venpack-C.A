# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    printax_code = fields.Integer(string='Código de tipo de pago en impresor', default='1', size = 2)
