# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _


class CustomAccountMove(models.Model):
    _inherit = 'account.move'
    _description = "Modificar modulo de account move"

    x_purchase_order = fields.Char(string="Orden de Compra", compute='_get_purchase_order', store=True)
    x_dispatch_number_tracking = fields.Char(string="Guia de Despacho")
    x_IM_vaucher_number = fields.Char(string="No Comprobante IM")
    x_npedido = fields.Char(string="No Pedido", compute='_get_purchase_order', store=True)

    x_retencion_usd = fields.Float(
        string="Retención",
        compute='_compute_retencion',
        store=True,
        default=0.0
    )

    @api.depends('x_impuesto', 'company_id')
    def _compute_retencion(self):
        for rec in self:
            retencion = 0.0
            if rec.x_impuesto:
                company_id = rec.company_id.id
                if company_id == 1:
                    retencion = rec.x_impuesto * 0.75
                elif company_id in [3, 6]:
                    retencion = rec.x_impuesto
            rec.x_retencion_usd = retencion

    @api.depends('invoice_origin')
    def _get_purchase_order(self):
        for rec in self:
            if rec.invoice_origin:
                pedido = self.env['sale.order'].search([('name', '=', rec.invoice_origin)])
                if pedido:
                    rec.x_purchase_order = pedido.x_purchase_order
                    rec.x_npedido = pedido.x_pedido
