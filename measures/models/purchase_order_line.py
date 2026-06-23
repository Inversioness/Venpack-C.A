# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_uom_sale = fields.Many2one(
        related='product_id.uom_id', 
        string='UdM Venta', 
        readonly=True
    )
    
    packaging_qty_info = fields.Float(
        related='product_packaging_id.qty', 
        string='Cant. Embalaje', 
        readonly=True
    )

    qty_uom = fields.Float(
        string='Unidad de Conversión',
        digits='Product Unit of Measure',
        default=0.0
    )

    qty_wherehouse = fields.Float(
        string='Recibido Almacén',
        digits='Product Unit of Measure',
        compute='_compute_qty_wherehouse',
        store=True
    )

    qty_dispatch = fields.Float(
        string='Por Despachar',
        digits='Product Unit of Measure',
        compute='_compute_qty_dispatch',
        store=True
    )

    qty_receive = fields.Float(
        string='Por Recibir',
        digits='Product Unit of Measure',
        compute='_compute_qty_receive',
        store=True
    )

    @api.depends('qty_received', 'product_uom')
    def _compute_qty_wherehouse(self):
        """ Calcula la cantidad recibida convertida según el ratio de la UdM """
        for line in self:
            if line.qty_received and line.product_uom and line.product_uom.ratio > 0:
                line.qty_wherehouse = line.qty_received / line.product_uom.ratio
            else:
                line.qty_wherehouse = 0.0

    @api.depends('qty_received', 'product_qty')
    def _compute_qty_dispatch(self):
        """ Calcula la cantidad por despachar """
        for line in self:
            if line.qty_received and line.product_qty:
                line.qty_dispatch = line.product_qty - line.qty_received
            else:
                line.qty_dispatch = 0.0

    @api.depends('qty_wherehouse', 'qty_uom')
    def _compute_qty_receive(self):
        """ Calcula la cantidad por recibir """
        for line in self:
            if line.qty_wherehouse and line.product_qty:
                line.qty_receive = line.qty_uom - line.qty_wherehouse
            else:
                line.qty_receive = 0.0

    # --- Lógica de Recálculo Bidireccional ---
    @api.onchange('qty_uom', 'product_uom')
    def _onchange_qty_uom(self):
        """ Si cambia mi variable manual, se actualiza la cantidad de Odoo """
        for line in self:
            if line.qty_uom and line.product_uom and line.product_uom.ratio > 0:
                line.product_qty = line.qty_uom * line.product_uom.ratio
            elif line.qty_uom == 0:
                line.product_qty = 0.0
    
    @api.onchange('product_qty')
    def _onchange_product_qty_inverse(self):
        """ Si cambia la cantidad de Odoo, se actualiza mi variable manual """
        for line in self:
            # Evitamos división por cero revisando el ratio
            if line.product_qty and line.product_uom and line.product_uom.ratio > 0:
                line.qty_uom = line.product_qty / line.product_uom.ratio
            elif line.product_qty == 0:
                line.qty_uom = 0.0