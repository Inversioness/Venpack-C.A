from odoo import models, fields, api
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
        """
        Inyectamos la tasa en el contexto para que cualquier llamada oculta a _convert 
        dentro del módulo de mai_igtf_venezuela use la tasa manual.
        """
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
        return res