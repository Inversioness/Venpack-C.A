# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CustomSaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Modificar modulo de sale order"

    x_purchase_order = fields.Char(string="Orden de Compra")
    x_payment_method = fields.Char(string="Forma de Pago")
    # x_totalkd = fields.Float(
    #     string="Total Kilos Despachados",
    #     compute="_compute_totalkd",
    #     store=True,
    #     default=0,
    # )
    # x_totaluds_despachadas = fields.Float(
    #     string="Total Unidades Despachadas",
    #     compute="_compute_totalusd_despachadas",
    #     store=True,
    #     default=0,
    # )

    product_id = fields.Many2one(
        "product.product",
        string="Nombre del Producto",
        compute="_compute_first_line_fields",
        store=True,
    )
    x_presentacion = fields.Selection(
        selection=[
            ("01", "Bobinas"),
            ("02", "Bolsas"),
            ("03", "Banderines"),
            ("04", "Sacos"),
            ("05", "Clisé"),
            ("06", "Maquila"),
        ],
        string="Presentación",
        compute="_compute_first_line_fields",
        store=True,
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unidad de Medida",
        compute="_compute_first_line_fields",
        store=True,
    )
    x_tipop = fields.Selection(
        selection=[
            ("01", "Banderín"),
            ("02", "Bobinas agricultura e invernadero"),
            ("03", "Bobinas anaquel"),
            ("04", "Bobinas empaque automático"),
            ("05", "Bobinas Multiusos"),
            ("06", "Bolsas comerciales"),
            ("07", "Bolsas sellado de fondo"),
            ("08", "Bolsas sellado lateral"),
            ("09", "Bolsas pan y pañal"),
            ("10", "Bolsas pollo"),
            ("11", "Saco valvulado"),
            ("12", "Saco industrial"),
            ("13", "Saco industrial flow pack"),
            ("14", "Bolsas con zipper"),
            ("15", "Bobina de stretch"),
            ("16", "Clisé"),
            ("17", "Maquila"),
            ("18", "Bolsa de empaque al vacío"),
            ("19", "Productos Estándar"),
        ],
        string="Tipo de Producto",
        compute="_compute_first_line_fields",
        store=True,
    )
    x_tipox = fields.Selection(
        selection=[
            ("01", "Extrusión"),
            ("02", "Coextrusión"),
            ("03", "Material de terceros"),
        ],
        string="Tipo de Extrusión",
        compute="_compute_first_line_fields",
        store=True,
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

                # Asignar valores directamente desde el producto
                order.x_presentacion = first_line.product_id.x_presentacion or False
                order.uom_id = first_line.product_id.uom_id or False
                order.x_tipop = first_line.product_id.x_tipop or False
                order.x_tipox = first_line.product_id.x_tipox or False
            else:
                order.product_id = False
                order.x_presentacion = False
                order.uom_id = False
                order.x_tipop = False
                order.x_tipox = False
