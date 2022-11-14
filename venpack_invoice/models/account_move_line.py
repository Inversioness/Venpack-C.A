# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _


class CustomAccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = "Modificar modulo de account move line "

    unit_price_without_tax = fields.Float(compute='calculate_unit_price_without_tax', store=True, string='Precio unitario sin impuestos')

    @api.depends('price_unit')
    def calculate_unit_price_without_tax(self):
        for record in self:
            if record.tax_ids:
                for ti in record.tax_ids:
                    if ti.x_tipoimpuesto == 'IVA':
                        record.unit_price_without_tax = round(record.price_unit / ((100 + ti.amount)/100), 2)
                    else:
                        record.unit_price_without_tax = record.price_unit
            else:
                record.unit_price_without_tax = record.price_unit
