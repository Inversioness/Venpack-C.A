# -*- coding: utf-8 -*-
from odoo import api, models
import logging

_logger = logging.getLogger(__name__)

class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        # 1. Intentamos obtener los datos originales
        try:
            data = super(ReportSaleDetails, self).get_sale_details(date_start, date_stop, config_ids, session_ids)
        except Exception as e:
            _logger.error("Error en super de get_sale_details: %s", str(e))
            data = {}
            
        if not isinstance(data, dict):
            data = {}

        #  BUSCAR DATOS REALES SI EL SUPER FALLÓ O VIENE VACÍO
        # Si no hay productos o el total es 0, forzamos la búsqueda manual
        if not data.get('products') and session_ids:
            orders = self.env['pos.order'].search([
                ('state', 'in', ['paid', 'invoiced', 'done']),
                ('session_id', 'in', session_ids)
            ])
            
            # Recalculamos lo básico para que el reporte no salga en blanco
            data.update({
                'total_paid': sum(orders.mapped('amount_total')),
                'discount_amount': sum(orders.mapped('amount_total')) * 0.05,
                'products': [],
                'payments': [],
                'taxes': [],
            })

        if 'total_paid' not in data:
            data['total_paid'] = 0.0

        user_currency = self.env.company.currency_id
        if 'currency' not in data or not isinstance(data.get('currency'), dict):
            data['currency'] = {
                'symbol': user_currency.symbol,
                'position': user_currency.position,
                'decimals': user_currency.decimal_places,
                'precision': user_currency.decimal_places,
            }
        
        data['currency']['total_paid'] = data['total_paid']

        # 5. LÓGICA DE MONEDA DUAL
        pos_session = self.env['pos.session'].browse(session_ids) if session_ids else False
        rate = pos_session[0].tax_today if pos_session and pos_session[0].tax_today != 0 else 1.0
        currency_dif = getattr(self.env.company, 'currency_id_dif', user_currency)

        data.update({
            'total_paid_ref': currency_dif.round(data['total_paid'] / rate) if rate else 0.0,
            'rate_today': rate,
            'symbol_ref': currency_dif.symbol,
            'currency_precision_ref': currency_dif.decimal_places or 2,
        })

        return data