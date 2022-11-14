# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
import json
from datetime import datetime
# from odoo.exceptions import ValidationError


class CustomAccountMove(models.Model):
    _inherit = 'account.move'
    _description = "Modificar modulo de account move"

    third_party_account_payment = fields.Boolean(related='partner_id.third_party_account_payment')
    fiscal_provider = fields.Many2one('res.partner', compute='select_provider', store=True, string='Proveedor Fiscal', readonly=False)
    x_tasa = fields.Float(compute='_get_currency_rate', store=True, string='Tasa')
    # x_invoice_payment = fields.Date(string='Fecha de pago', store=True, index=True, compute='_compute_invoice_payments')
    x_payment_ids = fields.Many2many('account.payment', string='Ordenes de Pago', store=True, compute='_compute_invoice_payments')

    @api.depends('invoice_payments_widget', 'invoice_outstanding_credits_debits_widget')
    def _compute_invoice_payments(self):
        print('pase por aqui')
        for rec in self:
            dates = []
            payment_ids = []
            date = False
            # rec.x_invoice_payment = False
            rec.x_payment_ids = False
            if json.loads(rec.invoice_payments_widget):
                for line in json.loads(rec.invoice_payments_widget)['content']:
                    # dates.append(line['date'])
                    if line['account_payment_id']:
                        payment_ids.append(line['account_payment_id'])
                # date = datetime.strptime(sorted(dates, reverse=True)[0], '%Y-%m-%d').date()
                # rec.x_invoice_payment = date
                rec.x_payment_ids = [(6, 0, payment_ids)]



    @api.depends('currency_id', 'manual_currency_rate', 'invoice_date', 'date', 'manual_currency_rate_active')
    def _get_currency_rate(self):
        for record in self:
            if record.manual_currency_rate_active:
                if record.manual_currency_rate != 0:
                    if record.company_id.currency_id.name == 'VES':
                        record.x_tasa = round(1/record.manual_currency_rate, 4)
                    else:
                        record.x_tasa = round(record.manual_currency_rate, 4)
                else:
                    record.x_tasa = 0.0
            else:
                if record.move_type and record.move_type in ['out_invoice', 'out_refund', 'entry', 'out_receipt']:
                    date = record.date
                elif record.move_type and record.move_type in ['in_invoice', 'in_refund', 'in_receipt']:
                    if record.state != 'posted' and record.invoice_date == False:
                        date = record.date
                    else:
                        date = record.invoice_date
                else:
                    date = record.date

                if date:
                    if record.currency_id == record.company_id.currency_id:
                        if record.company_id.currency_id.name == 'VES':
                            rate_id = self.env['res.currency.rate'].search(
                                [('currency_id', '=', 'USD'), ('name', '=', date)], limit=1)
                        else:
                            rate_id = self.env['res.currency.rate'].search(
                                [('currency_id', '=', 'VES'), ('name', '=', date)], limit=1)
                    else:
                        rate_id = self.env['res.currency.rate'].search([('currency_id', '=', record.currency_id.id), ('name', '=', date)], limit=1)

                    if not rate_id:
                        record.x_tasa = 0.0
                    else:
                        if record.company_id.currency_id.name == 'VES':
                            record.x_tasa = rate_id.inverse_company_rate
                        else:
                            record.x_tasa = rate_id.company_rate
                else:
                    raise exceptions.ValidationError(_("No se ha configurado una fecha para el documento " + record.name))



    @api.depends('partner_id')
    def select_provider(self):
        for record in self:
            record.fiscal_provider = record.partner_id.id

    @staticmethod
    def transform_and_group_by_item(data: list, item_group: str, sub_item_group: str) -> dict:
        data_transform = {}
        if data:
            for elem in data:
                if elem[item_group]:
                    for elem2 in elem[item_group]:
                        if elem2[sub_item_group] == 'ISLR':
                            if elem2['name'] in data_transform:
                                data_transform[elem2['name']].append(elem)
                            else:
                                data_transform[elem2['name']] = [elem]
                else:
                    print('No existe tax para la linea de venta')
        else:
            print('No existe lineas de venta')

        return data_transform

    @api.model
    def create(self, vals_list):
        res = super(CustomAccountMove, self).create(vals_list)
        print(res)
        tax_nd = []

        if res.fiscal_provider.x_tipopersona and res.fiscal_provider.x_tipopersona == 'Natural Domiciliado':
            for invoice_line in res.invoice_line_ids:
                if invoice_line.tax_ids:
                    for tax in invoice_line.tax_ids:
                        if tax.x_beneficiario and tax.x_beneficiario == 'Natural Domiciliado':
                            if tax not in tax_nd:
                                tax_nd.append(tax)
            if tax_nd:
                for tnd in tax_nd:
                    to_write = []
                    for line in res.line_ids:
                        if line.name == tnd.name:
                            to_write.append((1, line.id, {
                                'credit': round(line.credit - tnd.x_rebaja, 2)
                            }))
                        if line.account_id.id == res.fiscal_provider.property_account_payable_id.id:
                            to_write.append((1, line.id, {
                                'credit': round(line.credit + tnd.x_rebaja, 2)
                            }))
                    res.write({'line_ids': to_write})
        print(res)
        return res

    def write(self, values):
        res = super(CustomAccountMove, self).write(values)
        print(values)
        tax_nd = []

        if self.fiscal_provider.x_tipopersona and self.fiscal_provider.x_tipopersona == 'Natural Domiciliado' and 'line_ids' in values:
        # if self.fiscal_provider.x_tipopersona and self.fiscal_provider.x_tipopersona == 'Natural Domiciliado':
            for invoice_line in self.invoice_line_ids:
                if invoice_line.tax_ids:
                    for tax in invoice_line.tax_ids:
                        if tax.x_beneficiario and tax.x_beneficiario == 'Natural Domiciliado':
                            for val in values['line_ids']:
                                if isinstance(val[1], str) and 'virtual' in val[1] and val[2]['name'] == tax.name:
                                    if tax not in tax_nd:
                                        tax_nd.append(tax)
            if tax_nd:
                for tnd in tax_nd:
                    to_write = []
                    for line in self.line_ids:
                        if line.name == tnd.name:
                            to_write.append((1, line.id, {
                                'credit': round(line.credit - tnd.x_rebaja, 2)
                            }))
                        if line.account_id.id == self.fiscal_provider.property_account_payable_id.id:
                            to_write.append((1, line.id, {
                                'credit': round(line.credit + tnd.x_rebaja, 2)
                            }))
                    self.write({'line_ids': to_write})
        return res

    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False

            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue

            pay_term_lines = move.line_ids\
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('parent_state', '=', 'posted'),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]

            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

            if move.is_inbound():
                domain.append(('balance', '<', 0.0))
                payments_widget_vals['title'] = _('Outstanding credits')
            else:
                domain.append(('balance', '>', 0.0))
                payments_widget_vals['title'] = _('Outstanding debits')

            for line in self.env['account.move.line'].search(domain):

                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = move.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )

                if move.currency_id.is_zero(amount):
                    continue

                payments_widget_vals['content'].append({
                    'journal_name': line.ref or line.move_id.name,
                    'amount': amount,
                    'currency': move.currency_id.symbol,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'position': move.currency_id.position,
                    'digits': [69, move.currency_id.decimal_places],
                    'date': fields.Date.to_string(line.date),
                    'invoice_date': line.move_id.invoice_date.strftime('%d/%m/%Y') if line.move_id.x_tipodoc == 'Nota de Crédito' else line.move_id.date.strftime('%d/%m/%Y'),
                    'name': line.move_id.name,
                    'account_payment_id': line.payment_id.id,
                })

            if not payments_widget_vals['content']:
                continue

            move.invoice_outstanding_credits_debits_widget = json.dumps(payments_widget_vals)
            move.invoice_has_outstanding = True