# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    x_amount_retencion = fields.Float(string="Importe", digits=(16, 2))
    amount_bs = fields.Float(string="Importe Bs", digits=(16, 2))
    x_tasa = fields.Float(string="Tasa", digits=(16, 6))
    
    x_payment_difference = fields.Float(string="Diferencia en pago", compute='_compute_x_payment_difference')
    manual_currency_rate_active = fields.Boolean(string="Aplica tasa manual")
    manual_currency_rate = fields.Float(string="Rate Manual", digits=(16, 10))

    is_retencion_iva = fields.Boolean(compute='_compute_is_retencion_iva')
    is_ves_currency = fields.Boolean(compute='_compute_is_ves_currency')

    @api.depends('journal_id')
    def _compute_is_retencion_iva(self):
        for rec in self:
            name = rec.journal_id.name.upper() if rec.journal_id else ''
            rec.is_retencion_iva = ('RETENCI' in name and 'IVA' in name)

    @api.depends('currency_id')
    def _compute_is_ves_currency(self):
        for rec in self:
            rec.is_ves_currency = (rec.currency_id and rec.currency_id.name == 'VES')

    @api.depends('source_amount', 'source_amount_currency', 'x_amount_retencion')
    def _compute_x_payment_difference(self):
        for rec in self:
            total_factura = abs(rec.source_amount_currency) if rec.source_amount_currency else abs(rec.source_amount)
            usd_redondeado = round(rec.x_amount_retencion, 2)
            rec.x_payment_difference = total_factura - usd_redondeado

    @api.onchange('journal_id', 'currency_id', 'payment_date')
    def _onchange_journal_retencion(self):
        for rec in self:
            if rec.is_retencion_iva and not rec.is_ves_currency:
                moves = rec.line_ids.mapped('move_id')
                if not moves and self._context.get('active_ids'):
                    moves = self.env['account.move'].browse(self._context.get('active_ids'))
                
                if moves and 'x_retencion_usd' in moves[0]._fields:
                    rec.x_amount_retencion = round(moves[0].x_retencion_usd, 2)
                else:
                    rec.x_amount_retencion = 0.0

                usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
                date_to_use = rec.payment_date or fields.Date.context_today(rec)

                rate_obj = self.env['res.currency.rate'].sudo().search([
                    ('currency_id', '=', usd_currency.id),
                    ('name', '<=', date_to_use)
                ], limit=1, order='name desc')

                tasa_odoo = rate_obj.rate if rate_obj and rate_obj.rate > 0 else 1.0
                tasa_humana = (1 / tasa_odoo) if tasa_odoo > 0 else 1.0

                if rec.amount_bs <= 0:
                    rec.x_tasa = tasa_humana
                    usd_redondeado = round(rec.x_amount_retencion, 2)
                    rec.amount_bs = round(usd_redondeado * tasa_humana, 2)
                    rec.manual_currency_rate = tasa_odoo
                    rec.manual_currency_rate_active = True
            else:
                rec.manual_currency_rate_active = False
                rec.amount_bs = 0.0
                rec.x_tasa = 0.0
                rec.x_amount_retencion = 0.0

    @api.onchange('amount_bs', 'x_amount_retencion')
    def _onchange_calculo_tasa(self):
        for rec in self:
            usd_redondeado = round(rec.x_amount_retencion, 2)
            if rec.is_retencion_iva and not rec.is_ves_currency:
                if rec.amount_bs > 0 and usd_redondeado > 0:
                    tasa_correcta = rec.amount_bs / usd_redondeado
                    rec.x_tasa = tasa_correcta
                    rec.manual_currency_rate = 1 / tasa_correcta
                    rec.manual_currency_rate_active = True

    def action_create_payments(self):
        for rec in self:
            if rec.is_retencion_iva and not rec.is_ves_currency:
                usd_redondeado = round(rec.x_amount_retencion, 2)
                if rec.amount_bs > 0 and usd_redondeado > 0:
                    tasa_correcta = rec.amount_bs / usd_redondeado
                    rec.write({
                        'amount': usd_redondeado,
                        'x_tasa': tasa_correcta,
                        'manual_currency_rate': 1 / tasa_correcta,
                        'manual_currency_rate_active': True,
                    })
        return super(AccountPaymentRegister, self).action_create_payments()

    def _create_payment_vals_from_wizard(self, batch_result):
        vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        if self.is_retencion_iva and not self.is_ves_currency:
            usd_redondeado = round(self.x_amount_retencion, 2)
            if usd_redondeado > 0:
                vals['amount'] = usd_redondeado
            
            if self.amount_bs > 0 and usd_redondeado > 0:
                tasa_correcta = self.amount_bs / usd_redondeado
                vals.update({
                    'manual_currency_rate_active': True,
                    'manual_currency_rate': 1 / tasa_correcta,
                    'x_tasa': tasa_correcta,
                    'manual_rate_date': self.payment_date or fields.Date.context_today(self),
                })
        return vals

    def _create_payments(self):
        self.ensure_one()
        usd_redondeado = round(self.x_amount_retencion, 2)
        
        if self.is_retencion_iva and self.amount_bs > 0 and usd_redondeado > 0:
            tasa_correcta = self.amount_bs / usd_redondeado
            self = self.with_context(
                orden_suprema_tasa_manual=True,
                orden_suprema_tasa_odoo=1 / tasa_correcta,
                orden_suprema_tasa_humana=tasa_correcta,
                orden_suprema_monto_usd=usd_redondeado,
                manual_currency_rate=1 / tasa_correcta,
                manual_currency_rate_active=True,
                check_move_validity=False
            )
        return super(AccountPaymentRegister, self)._create_payments()


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    manual_currency_rate_active = fields.Boolean(string="Aplica tasa manual")
    manual_rate_date = fields.Date(string="Fecha de Tasa Manual")
    manual_currency_rate = fields.Float(string="Rate Manual", digits=(16, 10))

    @api.model_create_multi
    def create(self, vals_list):
        ctx = self._context
        if ctx.get('orden_suprema_tasa_manual'):
            for vals in vals_list:
                if ctx.get('orden_suprema_monto_usd'):
                    vals['amount'] = ctx.get('orden_suprema_monto_usd')
                vals['manual_currency_rate_active'] = True
                vals['manual_currency_rate'] = ctx.get('orden_suprema_tasa_odoo')
                if 'x_tasa' in self._fields:
                    vals['x_tasa'] = ctx.get('orden_suprema_tasa_humana')
                    
        payments = super(AccountPayment, self).create(vals_list)
        
        if ctx.get('orden_suprema_tasa_manual'):
            payments.write({
                'amount': ctx.get('orden_suprema_monto_usd'),
                'manual_currency_rate_active': True,
                'manual_currency_rate': ctx.get('orden_suprema_tasa_odoo'),
            })
            if 'x_tasa' in payments._fields:
                payments.write({'x_tasa': ctx.get('orden_suprema_tasa_humana')})
                
            for pay in payments:
                if pay.move_id:
                    pay.move_id.write({
                        'manual_currency_rate_active': True,
                        'manual_currency_rate': ctx.get('orden_suprema_tasa_odoo'),
                    })
                    if 'x_tasa' in pay.move_id._fields:
                        pay.move_id.write({'x_tasa': ctx.get('orden_suprema_tasa_humana')})
                        
        return payments

    def action_post(self):
        context_to_pass = {}
        if self.manual_currency_rate_active and self.manual_currency_rate > 0:
            context_to_pass.update({
                'manual_currency_rate': self.manual_currency_rate,
                'manual_currency_rate_active': True,
                'check_move_validity': False,
            })

        res = super(AccountPayment, self.with_context(**context_to_pass)).action_post()

        for pay in self:
            if getattr(pay, 'igtf_move_id', False) and pay.manual_currency_rate_active:
                pay.igtf_move_id.write({
                    'manual_currency_rate': pay.manual_currency_rate,
                    'manual_currency_rate_active': True,
                })
        return res