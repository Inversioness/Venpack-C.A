# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _


class CustomSaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = "Modificar modulo de sale order"

    x_purchase_order = fields.Char(string="Orden de Compra")
    x_payment_method = fields.Char(string="Forma de Pago")

