# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import _, api, fields, models


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        company = self.env.company
        if company.backdate_for_stock_move_so or company.backdate_for_stock_move or company.backdate_for_picking:
            for rec in res:
                if rec.stock_move_id.date:
                    self.env.cr.execute("""
                            UPDATE stock_valuation_layer SET create_date=%s where id=%s; 
                        """, (rec.stock_move_id.date, rec.id))
        return res
