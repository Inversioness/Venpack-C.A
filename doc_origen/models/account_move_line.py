# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Creamos un nuevo campo computado para consolidar el origen real
    origen_documento_real = fields.Char(
        string='Origen Real', 
        compute='_compute_origen_documento_real',
        store=False  # Al ser False, se calcula al vuelo y no llena la base de datos innecesariamente
    )

    # Transformado a campo computado para propagarse por todo el flujo del documento
    x_bl_custom = fields.Char(
        string='Número de B/L - AWB',
        compute='_compute_x_bl_custom',
        store=False,
        readonly=True
    )

    @api.depends('move_id', 'move_id.invoice_origin', 'move_id.ref')
    def _compute_origen_documento_real(self):
        for line in self:
            origen = ""
            # 1. Si el asiento contable principal ya tiene el origen directo (ej: P00981 de la factura)
            if line.move_id.invoice_origin:
                origen = line.move_id.invoice_origin

            # 2. Si no tiene origen pero viene de inventario (ej: asientos Inv/2026/...)
            if not origen and line.move_id:
                # Usamos getattr de manera segura para evitar que lance AttributeError en apuntes sin inventario
                stock_move = getattr(line.move_id, 'stock_move_id', False) or getattr(line, 'stock_move_id', False)
                
                if stock_move:
                    if getattr(stock_move, 'purchase_line_id', False):
                        origen = stock_move.purchase_line_id.order_id.name
                    elif getattr(stock_move, 'sale_line_id', False):
                        origen = stock_move.sale_line_id.order_id.name
                    elif getattr(stock_move, 'picking_id', False) and stock_move.picking_id.origin:
                        origen = stock_move.picking_id.origin

            # 3. Plan de respaldo histórico basándose en texto si lo anterior no aplica
            if not origen and line.move_id.ref:
                if '/OUT/' in line.move_id.ref or '/IN/' in line.move_id.ref or '/INT/' in line.move_id.ref:
                    origen = line.move_id.ref
                elif line.move_id.ref != line.move_id.name:
                    origen = line.move_id.ref
            
            line.origen_documento_real = origen

    @api.depends('move_id', 'move_id.x_BL', 'origen_documento_real')
    def _compute_x_bl_custom(self):
        for line in self:
            # 1. Si el asiento actual ya tiene el Número de B/L (Caso Facturas), lo usamos directamente
            if line.move_id.x_BL:
                line.x_bl_custom = line.move_id.x_BL
            # 2. Si está vacío (Caso Inventario/Recepciones), lo buscamos a través del Origen común
            elif line.origen_documento_real:
                # Buscamos cualquier factura/asiento en el sistema con el mismo origen que sí tenga el campo x_BL lleno
                asiento_con_bl = self.env['account.move'].sudo().search([
                    ('invoice_origin', '=', line.origen_documento_real),
                    ('x_BL', '!=', False)
                ], limit=1)
                
                if asiento_con_bl:
                    line.x_bl_custom = asiento_con_bl.x_BL
                else:
                    line.x_bl_custom = False
            else:
                line.x_bl_custom = False