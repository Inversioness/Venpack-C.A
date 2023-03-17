# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
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

    # @api.depends('move_id.line_ids.matched_debit_ids', 'move_id.line_ids.matched_credit_ids')
    # def _compute_stat_buttons_from_reconciliation(self):
    #     ''' Retrieve the invoices reconciled to the payments through the reconciliation (account.partial.reconcile). '''
    #     stored_payments = self.filtered('id')
    #     if not stored_payments:
    #         self.reconciled_invoice_ids = False
    #         self.reconciled_invoices_count = 0
    #         self.reconciled_invoices_type = ''
    #         self.reconciled_bill_ids = False
    #         self.reconciled_bills_count = 0
    #         self.reconciled_statement_ids = False
    #         self.reconciled_statements_count = 0
    #         return
    #
    #     self.env['account.move'].flush()
    #     self.env['account.move.line'].flush()
    #     self.env['account.partial.reconcile'].flush()
    #
    #     self._cr.execute('''
    #             SELECT
    #                 payment.id,
    #                 ARRAY_AGG(DISTINCT invoice.id) AS invoice_ids,
    #                 invoice.move_type
    #             FROM account_payment payment
    #             JOIN account_move move ON move.id = payment.move_id
    #             JOIN account_move_line line ON line.move_id = move.id
    #             JOIN account_partial_reconcile part ON
    #                 part.debit_move_id = line.id
    #                 OR
    #                 part.credit_move_id = line.id
    #             JOIN account_move_line counterpart_line ON
    #                 part.debit_move_id = counterpart_line.id
    #                 OR
    #                 part.credit_move_id = counterpart_line.id
    #             JOIN account_move invoice ON invoice.id = counterpart_line.move_id
    #             JOIN account_account account ON account.id = line.account_id
    #             WHERE account.internal_type IN ('receivable', 'payable')
    #                 AND payment.id IN %(payment_ids)s
    #                 AND line.id != counterpart_line.id
    #                 AND invoice.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
    #             GROUP BY payment.id, invoice.move_type
    #         ''', {
    #         'payment_ids': tuple(stored_payments.ids)
    #     })
    #     query_res = self._cr.dictfetchall()
    #     self.reconciled_invoice_ids = self.reconciled_invoices_count = False
    #     self.reconciled_bill_ids = self.reconciled_bills_count = False
    #     for res in query_res:
    #         pay = self.browse(res['id'])
    #         if res['move_type'] in self.env['account.move'].get_sale_types(True):
    #             pay.reconciled_invoice_ids += self.env['account.move'].browse(res.get('invoice_ids', []))
    #             pay.reconciled_invoices_count = len(res.get('invoice_ids', []))
    #         else:
    #             pay.reconciled_bill_ids += self.env['account.move'].browse(res.get('invoice_ids', []))
    #             pay.reconciled_bills_count = len(res.get('invoice_ids', []))
    #
    #     self._cr.execute('''
    #             SELECT
    #                 payment.id,
    #                 ARRAY_AGG(DISTINCT counterpart_line.statement_id) AS statement_ids
    #             FROM account_payment payment
    #             JOIN account_move move ON move.id = payment.move_id
    #             JOIN account_journal journal ON journal.id = move.journal_id
    #             JOIN account_move_line line ON line.move_id = move.id
    #             JOIN account_account account ON account.id = line.account_id
    #             JOIN account_partial_reconcile part ON
    #                 part.debit_move_id = line.id
    #                 OR
    #                 part.credit_move_id = line.id
    #             JOIN account_move_line counterpart_line ON
    #                 part.debit_move_id = counterpart_line.id
    #                 OR
    #                 part.credit_move_id = counterpart_line.id
    #             WHERE account.id = payment.outstanding_account_id
    #                 AND payment.id IN %(payment_ids)s
    #                 AND line.id != counterpart_line.id
    #                 AND counterpart_line.statement_id IS NOT NULL
    #             GROUP BY payment.id
    #         ''', {
    #         'payment_ids': tuple(stored_payments.ids)
    #     })
    #     query_res = dict((payment_id, statement_ids) for payment_id, statement_ids in self._cr.fetchall())
    #
    #     for pay in self:
    #         statement_ids = query_res.get(pay.id, [])
    #         pay.reconciled_statement_ids = [(6, 0, statement_ids)]
    #         pay.reconciled_statements_count = len(statement_ids)
    #         if len(pay.reconciled_invoice_ids.mapped('move_type')) == 1 and pay.reconciled_invoice_ids[
    #             0].move_type == 'out_refund':
    #             pay.reconciled_invoices_type = 'credit_note'
    #         else:
    #             pay.reconciled_invoices_type = 'invoice'

