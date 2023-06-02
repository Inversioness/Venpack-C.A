# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError, ValidationError
import json
from datetime import datetime
# from odoo.exceptions import ValidationError


class CustomAccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = "Modificar modulo de account payment"

    document_date = fields.Date(string='Fecha Documento')
    affected_invoice_ids = fields.Many2many('account.move', compute='_compute_affected_invoice', string="Factura Afectada")

    @api.depends('reconciled_invoice_ids', 'reconciled_bill_ids')
    def _compute_affected_invoice(self):
        for record in self:
            if record.reconciled_invoice_ids:
                record.affected_invoice_ids = record.reconciled_invoice_ids
            elif record.reconciled_bill_ids:
                record.affected_invoice_ids = record.reconciled_bill_ids
            else:
                record.affected_invoice_ids = False

    def action_draft(self):
        ''' posted -> draft '''
        if self.reconciled_statements_count:
            raise UserError(_("El pago ya se encuentra conciliado, para modificar el pago debe romper la conciliacion y despues restablecer a borrador"))
        self.move_id.button_draft()
