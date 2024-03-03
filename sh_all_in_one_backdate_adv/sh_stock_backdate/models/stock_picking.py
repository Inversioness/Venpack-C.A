# -*- coding: utf-8 -*-
# Part of Softhealer Technologies

from odoo import fields, models,api
from datetime import date

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    remarks = fields.Text(string = "Remarks")
    is_remarks = fields.Boolean(related="company_id.remark_for_picking",string = "Is Remarks")
    is_remarks_mandatory = fields.Boolean(related="company_id.remark_mandatory_for_picking",string = "Is remarks mandatory")
    is_boolean = fields.Boolean()

    @api.onchange('scheduled_date')
    def onchange_scheduled_date(self):
        if str(self.scheduled_date.date()) < str(date.today()):
           self.is_boolean = True
        else:
            self.is_boolean = False

    @api.depends('move_ids.state', 'move_ids.date', 'move_type')
    def _compute_scheduled_date(self):
        for picking in self:
            if picking.company_id.backdate_for_stock_move_so and picking.sale_id:
                picking.scheduled_date = picking.sale_id.date_order
            elif picking.company_id.backdate_for_stock_move and picking.purchase_id:
                picking.scheduled_date = picking.purchase_id.date_approve
            elif picking.company_id.backdate_for_picking:
                continue
            else:
                moves_dates = picking.move_ids.filtered(
                    lambda move: move.state not in ('done', 'cancel')).mapped('date')
                if picking.move_type == 'direct':
                    picking.scheduled_date = min(
                        moves_dates, default=picking.scheduled_date or fields.Datetime.now())
                else:
                    picking.scheduled_date = max(
                        moves_dates, default=picking.scheduled_date or fields.Datetime.now())


    def write(self,vals):
        for rec in self:
            if 'date_done' in vals:
                vals['date_done'] = vals.get('scheduled_date') or rec.scheduled_date

            return super(StockPicking,self).write(vals)

    def _set_scheduled_date(self):
        for picking in self:
            # if picking.state in ('done', 'cancel'):
            #     raise UserError(_("You cannot change the Scheduled Date on a done or cancelled transfer."))
            picking.move_ids.write({'date': picking.scheduled_date})
