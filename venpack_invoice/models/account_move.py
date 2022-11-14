# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _


class CustomAccountMove(models.Model):
    _inherit = 'account.move'
    _description = "Modificar modulo de account move"

    x_purchase_order = fields.Char(string="Orden de Compra", compute='_get_purchase_order', store=True)
    x_dispatch_number_tracking = fields.Char(string="Guia de Despacho")
    x_IM_vaucher_number = fields.Char(string="No Comprobante IM")
    x_npedido = fields.Char(string="No Pedido", compute='_get_purchase_order', store=True)

    @api.depends('invoice_origin')
    def _get_purchase_order(self):
        for rec in self:
            if rec.invoice_origin:
                pedido = self.env['sale.order'].search([('name', '=', rec.invoice_origin)])
                if pedido:
                    rec.x_purchase_order = pedido.x_purchase_order
                    rec.x_npedido = pedido.x_pedido
