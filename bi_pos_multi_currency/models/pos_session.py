# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models, _, Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare

class PosSession(models.Model):
    _inherit = 'pos.session'
    _description = 'Point of Sale Session'

    def _create_combine_account_payment(self, payment_method, amounts, diff_amount):
        outstanding_account = payment_method.outstanding_account_id or self.company_id.account_journal_payment_debit_account_id
        destination_account = self._get_receivable_account(payment_method)

        if payment_method.journal_id.currency_id.name != 'VES':
            currency = payment_method.journal_id.currency_id
            amount = amounts['amount'] / currency.rate_ids[0].inverse_company_rate
        else:
            currency = payment_method.journal_id.currency_id
            amount = amounts['amount']

        if float_compare(amount, 0, precision_rounding=currency.rounding) < 0:
            # revert the accounts because account.payment doesn't accept negative amount.
            outstanding_account, destination_account = destination_account, outstanding_account

        account_payment = self.env['account.payment'].create({
            'amount': abs(amount),
            'journal_id': payment_method.journal_id.id,
            'force_outstanding_account_id': outstanding_account.id,
            'destination_account_id':  destination_account.id,
            'ref': _('Combine %s POS payments from %s') % (payment_method.name, self.name),
            'pos_payment_method_id': payment_method.id,
            'pos_session_id': self.id,
        })

        diff_amount_compare_to_zero = currency.compare_amounts(diff_amount, 0)
        if diff_amount_compare_to_zero != 0:
            self._apply_diff_on_account_payment_move(account_payment, payment_method, diff_amount)

        account_payment.action_post()
        return account_payment.move_id.line_ids.filtered(lambda line: line.account_id == account_payment.destination_account_id)
