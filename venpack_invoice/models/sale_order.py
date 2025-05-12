# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _


class CustomSaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Modificar modulo de sale order"

    x_purchase_order = fields.Char(string="Orden de Compra")
    x_payment_method = fields.Char(string="Forma de Pago")
    x_totalkd = fields.Float(
        string="Total Kilos Despachados",
        compute="_compute_totalkd",
        store=True,
        default=0,
    )
    x_totaluds_despachadas = fields.Float(
        string="Total Unidades Despachadas",
        compute="_compute_totalusd_despachadas",
        store=True,
        default=0,
    )

    product_id = fields.Many2one(
        "product.product",
        string="Nombre del Producto",
        compute="_compute_first_line_fields",
        store=True,
    )
    x_presentacion = fields.Char(
        string="Presentación", compute="_compute_first_line_fields", store=True
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unidad de Medida",
        compute="_compute_first_line_fields",
        store=True,
    )
    x_tipop = fields.Char(
        string="Tipo de Producto", compute="_compute_first_line_fields", store=True
    )
    x_tipox = fields.Char(
        string="Tipo de Extrusión", compute="_compute_first_line_fields", store=True
    )

    @api.depends("x_peso", "x_totaldespachado")
    def _compute_totalkd(self):
        for order in self:
            if order.x_peso > 0:
                order.x_totalkd = order.x_peso - order.x_totaldespachado
            else:
                order.x_totalkd = 0

    @api.depends("x_Totaluds", "x_udsdespachadasestimado")
    def _compute_totalusd_despachadas(self):
        for order in self:
            if order.x_Totaluds > 0:
                order.x_totaluds_despachadas = (
                    order.x_Totaluds - order.x_udsdespachadasestimado
                )
            else:
                order.x_totaluds_despachadas = 0

    @api.depends("order_line")
    def _compute_first_line_fields(self):
        for order in self:
            first_line = order.order_line[:1]
            if first_line and first_line.product_id:
                order.product_id = first_line.product_id
                order.x_presentacion = (
                    dict(first_line.product_id._fields["x_presentacion"].selection).get(
                        first_line.product_id.x_presentacion, ""
                    )
                    if first_line.product_id.x_presentacion
                    else ""
                )
                order.uom_id = first_line.product_id.uom_id or False
                order.x_tipop = (
                    dict(first_line.product_id._fields["x_tipop"].selection).get(
                        first_line.product_id.x_tipop, ""
                    )
                    if first_line.product_id.x_tipop
                    else ""
                )
                order.x_tipox = (
                    dict(first_line.product_id._fields["x_tipox"].selection).get(
                        first_line.product_id.x_tipox, ""
                    )
                    if first_line.product_id.x_tipox
                    else ""
                )
            else:
                order.product_id = False
                order.x_presentacion = ""
                order.uom_id = False
                order.x_tipop = ""
                order.x_tipox = ""
