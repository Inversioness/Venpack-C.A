# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    origen_documento_real = fields.Char(
        string='Origen', 
        compute='_compute_origen_documento_real',
        search='_search_origen_documento_real',
        store=False
    )

    x_bl_custom = fields.Char(
        string='Número de B/L - AWB',
        compute='_compute_x_bl_custom',
        search='_search_x_bl_custom',
        store=False,
        readonly=True
    )

    x_tasa_dinamica = fields.Float(
        string='Tasa Aplicada',
        compute='_compute_x_tasa_dinamica',
        store=False
    )

    importe_divisa_custom = fields.Monetary(
        string='Importe Divisa',
        compute='_compute_importe_divisa_custom',
        #currency_field='company_currency_id',
        store=False
    )

    @api.depends('move_id', 'move_id.move_type', 'move_id.invoice_line_ids')
    def _compute_x_tasa_dinamica(self):
        for line in self:
            tasa = 1.0
            if line.move_id:
                lineas_compra = line.move_id.invoice_line_ids.mapped('purchase_line_id')
                stock_move = getattr(line.move_id, 'stock_move_id', False) or getattr(line, 'stock_move_id', False)
                po = False
                
                if lineas_compra and lineas_compra[0].order_id:
                    po = lineas_compra[0].order_id
                elif stock_move and getattr(stock_move, 'purchase_line_id', False):
                    po = stock_move.purchase_line_id.order_id

                if po and hasattr(po, 'x_tasac'):
                    tasa = po.x_tasac or 1.0

                elif line.move_id.move_type in ('out_invoice', 'out_refund'):
                    lineas_venta = line.move_id.invoice_line_ids.mapped('sale_line_ids')
                    if lineas_venta and lineas_venta[0].order_id:
                        so = lineas_venta[0].order_id
                        if hasattr(so, 'x_tasav'):
                            tasa = so.x_tasav or 1.0

                if tasa == 1.0 and hasattr(line.move_id, 'x_tasa'):
                    tasa = line.move_id.x_tasa or 1.0
            
            line.x_tasa_dinamica = tasa

    @api.depends('debit', 'credit', 'x_tasa_dinamica')
    def _compute_importe_divisa_custom(self):
        for line in self:
            monto_local = line.debit - line.credit
            tasa = line.x_tasa_dinamica or 1.0

            if tasa > 0:
                line.importe_divisa_custom = monto_local / tasa
            else:
                line.importe_divisa_custom = monto_local

    @api.depends('move_id', 'move_id.invoice_origin', 'move_id.move_type', 'move_id.partner_id')
    def _compute_origen_documento_real(self):
        for line in self:
            origen = ""
            if line.move_id:
                if line.move_id.move_type in ('in_invoice', 'in_refund'):
                    lineas_compra = line.move_id.invoice_line_ids.mapped('purchase_line_id')
                    if lineas_compra:
                        origen = lineas_compra[0].order_id.name
                    elif line.move_id.invoice_origin:
                        origen_temp = line.move_id.invoice_origin.strip()
                        if origen_temp.startswith(('P', 'PO')):
                            po = self.env['purchase.order'].sudo().search([('name', '=', origen_temp)], limit=1)
                            if po and po.partner_id.name == line.move_id.partner_id.name:
                                origen = origen_temp
                else:
                    stock_move = getattr(line.move_id, 'stock_move_id', False) or getattr(line, 'stock_move_id', False)
                    if stock_move:
                        if getattr(stock_move, 'purchase_line_id', False):
                            origen = stock_move.purchase_line_id.order_id.name
                        elif getattr(stock_move, 'picking_id', False) and stock_move.picking_id.origin:
                            origen = stock_move.picking_id.origin
            
            line.origen_documento_real = origen

    @api.depends('move_id', 'move_id.x_BL', 'origen_documento_real')
    def _compute_x_bl_custom(self):
        for line in self:
            if line.move_id.x_BL:
                line.x_bl_custom = line.move_id.x_BL
            elif line.origen_documento_real and line.origen_documento_real.strip():
                asiento_con_bl = self.env['account.move'].sudo().search([
                    ('invoice_origin', '=', line.origen_documento_real),
                    ('move_type', 'in', ('in_invoice', 'in_refund')),
                    ('x_BL', '!=', False)
                ], limit=1)
                if asiento_con_bl:
                    line.x_bl_custom = asiento_con_bl.x_BL
                else:
                    line.x_bl_custom = False
            else:
                line.x_bl_custom = False

    def _search_origen_documento_real(self, operator, value):
        if operator not in ('=', 'ilike', 'like', '=like') or not value:
            return []

        value_clean = value.strip()
        pos = self.env['purchase.order'].sudo().search([('name', operator, value_clean)])
        if not pos:
            return [('id', '=', False)]

        move_ids_validos = []

        stock_moves = self.env['stock.move'].sudo().search([('purchase_line_id.order_id', 'in', pos.ids)])
        if stock_moves:
            asientos_inv = stock_moves.mapped('account_move_ids')
            move_ids_validos.extend(asientos_inv.ids)

        facturas_por_linea = self.env['account.move'].sudo().search([
            ('invoice_line_ids.purchase_line_id.order_id', 'in', pos.ids)
        ])
        move_ids_validos.extend(facturas_por_linea.ids)

        for po in pos:
            facturas_origen_texto = self.env['account.move'].sudo().search([
                ('invoice_origin', '=', po.name),
                ('move_type', 'in', ('in_invoice', 'in_refund'))
            ])
            for fac in facturas_origen_texto:
                if fac.partner_id.name == po.partner_id.name:
                    move_ids_validos.append(fac.id)

        return [('move_id', 'in', list(set(move_ids_validos)))]

    def _search_x_bl_custom(self, operator, value):
        if operator not in ('=', 'ilike', 'like', '=like') or not value:
            return []

        asientos_con_bl_directo = self.env['account.move'].sudo().search([
            ('x_BL', operator, value),
            ('move_type', 'in', ('in_invoice', 'in_refund'))
        ])
        
        origenes_validos = []
        for move in asientos_con_bl_directo:
            lineas_compra = move.invoice_line_ids.mapped('purchase_line_id')
            if lineas_compra:
                origenes_validos.append(lineas_compra[0].order_id.name)
            elif move.invoice_origin:
                origen_temp = move.invoice_origin.strip()
                if origen_temp.startswith(('P', 'PO')):
                    po = self.env['purchase.order'].sudo().search([('name', '=', origen_temp)], limit=1)
                    if po and po.partner_id.name == move.partner_id.name:
                        origenes_validos.append(origen_temp)
        
        movimientos_relacionados_ids = []
        if origenes_validos:
            pos = self.env['purchase.order'].sudo().search([('name', 'in', origenes_validos)])
            stock_moves = self.env['stock.move'].sudo().search([('purchase_line_id.order_id', 'in', pos.ids)])
            asientos_inv = stock_moves.mapped('account_move_ids')
            movimientos_relacionados_ids = asientos_inv.ids

        total_move_ids = asientos_con_bl_directo.ids + movimientos_relacionados_ids

        return [('move_id', 'in', list(set(total_move_ids)))]