# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    # Nuestro nuevo campo visual para reemplazar al estándar
    x_amount_retencion = fields.Float(string="Importe")
    
    amount_bs = fields.Float(string="Importe Bs")
    x_tasa = fields.Float(string="Tasa")
    manual_currency_rate_active = fields.Boolean(string="Aplica tasa manual")
    manual_currency_rate = fields.Float(string="Rate Manual")
    
    is_retencion_iva = fields.Boolean(compute='_compute_is_retencion_iva')
    is_ves_currency = fields.Boolean(compute='_compute_is_ves_currency')

    @api.depends('journal_id')
    def _compute_is_retencion_iva(self):
        for rec in self:
            rec.is_retencion_iva = (rec.journal_id and rec.journal_id.name == 'RETENCIÓN IVA')

    @api.depends('currency_id')
    def _compute_is_ves_currency(self):
        for rec in self:
            rec.is_ves_currency = (rec.currency_id.name == 'VES')

    @api.onchange('journal_id', 'currency_id', 'payment_date')
    def _onchange_journal_retencion(self):
        for rec in self:
            if rec.is_retencion_iva:
                if not rec.is_ves_currency:
                    # 1. Buscamos la factura y llenamos NUESTRO campo, dejando el de Odoo en paz
                    facturas = rec.line_ids.mapped('move_id')
                    if facturas and 'x_retencion_usd' in facturas[0]._fields:
                        rec.x_amount_retencion = facturas[0].x_retencion_usd
                    else:
                        rec.x_amount_retencion = 0.0

                    # 2. Calculamos la tasa del día
                    usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
                    date_to_use = rec.payment_date or fields.Date.context_today(rec)

                    rate_obj = self.env['res.currency.rate'].sudo().search([
                        ('currency_id', '=', usd_currency.id),
                        ('name', '<=', date_to_use)
                    ], limit=1, order='name desc')

                    tasa_del_dia = (1 / rate_obj.rate) if rate_obj and rate_obj.rate > 0 else 1.0

                    # 3. Asignamos cálculos en base a nuestro nuevo campo
                    rec.x_tasa = tasa_del_dia
                    rec.amount_bs = rec.x_amount_retencion * tasa_del_dia
                    rec.manual_currency_rate = tasa_del_dia
                    rec.manual_currency_rate_active = True
                
                else:
                    # Si es VES, apagamos todo
                    rec.manual_currency_rate_active = False
                    rec.amount_bs = 0.0
                    rec.x_tasa = 0.0
                    rec.x_amount_retencion = 0.0
            else:
                rec.manual_currency_rate_active = False
                rec.amount_bs = 0.0
                rec.x_tasa = 0.0
                rec.x_amount_retencion = 0.0

    @api.onchange('amount_bs')
    def _onchange_amount_bs_manual(self):
        for rec in self:
            # Importante: dividimos entre NUESTRO campo (x_amount_retencion)
            if rec.is_retencion_iva and not rec.is_ves_currency and rec.x_amount_retencion > 0 and rec.amount_bs > 0:
                tasa_calculada = rec.amount_bs / rec.x_amount_retencion
                rec.x_tasa = tasa_calculada
                rec.manual_currency_rate = tasa_calculada 
                rec.manual_currency_rate_active = True

    def _create_payments(self):
        self.ensure_one()
        
        # EL TRUCO: Justo antes de crear el pago, si es retención, 
        # forzamos a que el monto estándar de Odoo sea nuestra retención.
        if self.is_retencion_iva and self.x_amount_retencion > 0:
            self.amount = self.x_amount_retencion

        # Inyectamos contexto de tasa manual
        if not self.is_ves_currency and self.manual_currency_rate_active and getattr(self, 'manual_currency_rate', 0) > 0:
            self = self.with_context(
                manual_currency_rate=self.manual_currency_rate,
                manual_currency_rate_active=True,
                check_move_validity=False
            )
        return super(AccountPaymentRegister, self)._create_payments()
    
    
    """from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    manual_currency_rate_active = fields.Boolean(string="Aplica tasa manual")
    manual_rate_date = fields.Date(string="Fecha de Tasa Manual")

    @api.onchange('manual_currency_rate_active', 'manual_rate_date')
    def _onchange_set_manual_rate(self):
        if not self.manual_currency_rate_active or not self.manual_rate_date:
            return

        usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        
        if not usd_currency:
            _logger.error("No se encontró la moneda con nombre 'USD'")
            return

        # Buscamos la tasa usando el nuevo campo manual_rate_date
        rate_obj = self.env['res.currency.rate'].sudo().search([
            ('currency_id', '=', usd_currency.id),
            ('name', '=', self.manual_rate_date)
        ], limit=1, order='name desc')

        if rate_obj:
            self.manual_currency_rate = rate_obj.rate 
            
            if rate_obj.rate > 0:
                self.x_tasa = 1 / rate_obj.rate
        else:
            self.manual_currency_rate = 0.0
            self.x_tasa = 0.0

    def _prepare_move_line_default_vals_igft(self, write_off_line_vals=None):
        self.ensure_one()
        
        if not self.manual_currency_rate_active or self.manual_currency_rate <= 0:
            return super()._prepare_move_line_default_vals_igft(write_off_line_vals)

        igtf_amount_curr = self.igtf_amount
        if self.payment_type == 'outbound':
            igtf_amount_curr = -self.igtf_amount
        
        igtf_balance_ves = self.company_id.currency_id.round(igtf_amount_curr / self.manual_currency_rate)
        
        counterpart_amount_curr = -igtf_amount_curr
        counterpart_balance_ves = -igtf_balance_ves

        account_id = self.company_id.receivable_account_id.id if igtf_balance_ves < 0.0 else self.company_id.payable_account_id.id

        return [
            {
                'name': 'Comision IGTF Divisa',
                'amount_currency': igtf_amount_curr,
                'currency_id': self.currency_id.id,
                'debit': igtf_balance_ves if igtf_balance_ves > 0.0 else 0.0,
                'credit': -igtf_balance_ves if igtf_balance_ves < 0.0 else 0.0,
                'account_id': self.igtf_journal_id.default_account_id.id,
                # No pasamos 'rate' aquí, Odoo lo tomará del contexto del action_post
            },
            {
                'name': 'Contrapartida IGTF Divisa',
                'amount_currency': counterpart_amount_curr,
                'currency_id': self.currency_id.id,
                'debit': counterpart_balance_ves if counterpart_balance_ves > 0.0 else 0.0,
                'credit': -counterpart_balance_ves if counterpart_balance_ves < 0.0 else 0.0,
                'account_id': account_id,
            },
        ]

    def action_post(self):
       
        Inyectamos la tasa en el contexto para que cualquier llamada oculta a _convert 
        dentro del módulo de mai_igtf_venezuela use la tasa manual.
        
        if self.manual_currency_rate_active and self.manual_currency_rate > 0:
            self = self.with_context(
                manual_currency_rate=self.manual_currency_rate,
                manual_currency_rate_active=True,
                check_move_validity=False
            )
        
        res = super(AccountPayment, self).action_post()
        
        for pay in self:
            if pay.igtf_move_id and pay.manual_currency_rate_active:
                pay.igtf_move_id.write({
                    'manual_currency_rate': pay.manual_currency_rate,
                    'manual_currency_rate_active': True,
                })
        return res"""