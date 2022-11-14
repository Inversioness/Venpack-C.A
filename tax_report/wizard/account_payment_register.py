# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import json


class CustomAccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Custom Register Payment'

    tax_id = fields.Many2one('account.tax', string='Impuesto')
    tax_id_domain = fields.Char(compute="_compute_tax_id_domain", readonly=True, store=False,)
    tax_code = fields.Char(related='journal_id.tax_code', readonly=True)
    x_tasa = fields.Float(compute='_get_currency_rate', store=True, string='Tasa')

    # @api.depends('currency_id', 'manual_currency_rate', 'invoice_date', 'date', 'manual_currency_rate_active')
    @api.depends('payment_date', 'currency_id')
    def _get_currency_rate(self):
        for record in self:
            print(record)
            if record.payment_date:
                if record.currency_id == record.company_id.currency_id:
                    if record.company_id.currency_id.name == 'VES':
                        rate_id = self.env['res.currency.rate'].search(
                            [('currency_id', '=', 'USD'), ('name', '=', record.payment_date)], limit=1)
                    else:
                        rate_id = self.env['res.currency.rate'].search(
                            [('currency_id', '=', 'VES'), ('name', '=', record.payment_date)], limit=1)
                else:
                    rate_id = self.env['res.currency.rate'].search(
                        [('currency_id', '=', record.currency_id.id), ('name', '=', record.payment_date)], limit=1)

                if not rate_id:
                    raise exceptions.ValidationError(
                        _("No existe registro de tasa " + record.currency_id.name + " para la fecha " + str(record.payment_date)))
                else:
                    if record.company_id.currency_id.name == 'VES':
                        record.x_tasa = rate_id.inverse_company_rate
                    else:
                        record.x_tasa = rate_id.company_rate
            else:
                raise exceptions.ValidationError(
                    _("No se ha configurado una fecha para el documento " + record.name))

    @api.depends('journal_id')
    def _compute_tax_id_domain(self):
        for rec in self:
            if rec.journal_id.tax_code:
                rec.tax_id_domain = json.dumps([('x_tipoimpuesto', 'like', rec.journal_id.tax_code)])
            else:
                rec.tax_id_domain = json.dumps([('id', '=', False)])

    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id',
                 'payment_date', 'tax_id', 'line_ids')
    def _compute_amount(self):
        # res = super(CustomAccountPaymentRegister, self)._compute_amount()
        for wizard in self:
            if wizard.source_currency_id == wizard.currency_id:
                # Same currency.
                if wizard.tax_id:
                    if wizard.tax_id.x_tipoimpuesto == 'ISLR':
                        if wizard.tax_id.x_beneficiario == 'Natural Domiciliado':
                            wizard.amount = (wizard.line_ids[0].move_id.amount_untaxed * (
                                    abs(float(wizard.tax_id.description[:-1])) / 100)) - wizard.tax_id.x_rebaja
                        else:
                            wizard.amount = wizard.line_ids[0].move_id.amount_untaxed * (
                                    abs(float(wizard.tax_id.description[:-1])) / 100)
                    elif wizard.tax_id.x_tipoimpuesto == 'RIVA':
                        wizard.amount = wizard.line_ids[0].move_id.amount_tax * (abs(float(wizard.tax_id.description[:-1])) / 100)
                else:
                    wizard.amount = wizard.source_amount_currency
            elif wizard.currency_id == wizard.company_id.currency_id:
                # Payment expressed on the company's currency.
                if wizard.tax_id:
                    if wizard.tax_id.x_tipoimpuesto == 'ISLR':
                        if wizard.tax_id.x_beneficiario == 'Natural Domiciliado':
                            wizard.amount = (wizard.line_ids[0].move_id.amount_untaxed * (
                                    abs(float(wizard.tax_id.description[:-1])) / 100)) - wizard.tax_id.x_rebaja
                        else:
                            wizard.amount = wizard.line_ids[0].move_id.amount_untaxed * (
                                    abs(float(wizard.tax_id.description[:-1])) / 100)
                    elif wizard.tax_id.x_tipoimpuesto == 'RIVA':
                        wizard.amount = wizard.line_ids[0].move_id.amount_tax * (
                                    abs(float(wizard.tax_id.description[:-1])) / 100)
                else:
                    wizard.amount = wizard.source_amount
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                if wizard.tax_id:
                    if wizard.tax_id.x_tipoimpuesto == 'ISLR':
                        if wizard.tax_id.x_beneficiario == 'Natural Domiciliado':
                            wizard.amount = (wizard.line_ids[0].move_id.amount_untaxed * (
                                    abs(float(wizard.tax_id.description[:-1])) / 100)) - wizard.tax_id.x_rebaja
                        else:
                            wizard.amount = wizard.line_ids[0].move_id.amount_untaxed * (
                                        abs(float(wizard.tax_id.description[:-1])) / 100)
                    elif wizard.tax_id.x_tipoimpuesto == 'RIVA':
                        wizard.amount = wizard.line_ids[0].move_id.amount_tax * (
                                    abs(float(wizard.tax_id.description[:-1])) / 100)
                else:
                    if wizard.manual_currency_rate_active and wizard.manual_currency_rate > 0:
                        currency_rate = wizard.manual_currency_rate
                        amount_payment_currency = wizard.source_amount * currency_rate
                    else:
                        amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount,
                                                                                         wizard.currency_id,
                                                                                         wizard.company_id,
                                                                                         wizard.payment_date)
                    wizard.amount = amount_payment_currency
