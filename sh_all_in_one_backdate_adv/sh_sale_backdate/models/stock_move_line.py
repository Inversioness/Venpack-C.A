# -*- coding: utf-8 -*-
# Part of Softhealer Technologies

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # date = fields.Datetime(
    #     'Date', default=fields.Datetime.now, related="move_id.date")

    remarks_for_sale = fields.Text(
        string="Remarks for sale", related="move_id.remarks_for_sale")
    is_remarks_for_sale = fields.Boolean(
        related="company_id.remark_for_sale_order", string="Is Remarks for sale")

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for rec in self:
            if rec.company_id.backdate_for_picking or (
            rec.company_id.backdate_for_stock_move_so and rec.picking_id.sale_id) or (
            rec.company_id.backdate_for_stock_move and rec.picking_id.purchase_id):
                rec.date = rec.picking_id.scheduled_date or rec.move_id.date
        return res
