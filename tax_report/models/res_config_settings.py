# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fiscal_period_type = fields.Selection([('date', 'Selector fecha'), ('month', 'Mensual')], default='date',
                                          string="Tipo de Periocidad Libro de Ventas/Compras",
                                          )
    # fiscal_period_type = fields.Selection([('date', 'Selector fecha'), ('month', 'Mensual')], default='date',
    #                                       string="Tipo de Periocidad Libro de Ventas/Compras",
    #                                       config_parameter='tax_report.fiscal_period_type')

    @api.model
    def get_values(self):
        res = super().get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(fiscal_period_type=get_param('tax_report.fiscal_period_type'))
        return res

    def set_values(self):
        res = super().set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('tax_report.fiscal_period_type', self.fiscal_period_type)
        return res
