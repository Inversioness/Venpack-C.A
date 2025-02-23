# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _


class CustomSaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = "Modificar modulo de sale order"

    x_purchase_order = fields.Char(string="Orden de Compra")
    x_payment_method = fields.Char(string="Forma de Pago")
    x_totalkd = fields.Float(string="Total Kilos Despachados", compute="_compute_totalkd", store=True, default=0)
    x_totalusd_despachadas = fields.Float(string="Total Unidades Despachadas", compute="_compute_totalusd_despachadas", store=True, default=0)

    @api.depends('x_peso', 'x_totaldespachado')
    def _compute_totalkd(self):
        for order in self:
            if order.x_peso > 0:
                order.x_totalkd = order.x_peso - order.x_totaldespachado
            else:
                order.x_totalkd = 0

    @api.depends('x_Totalusd', 'x_usddespachadasestimado')
    def _compute_totalusd_despachadas(self):
        for order in self:
            if order.x_Totalusd > 0:
                order.x_totalusd_despachadas = order.x_Totaluds - order.x_usddespachadasestimado
            else:
                order.x_totalusd_despachadas = 0
