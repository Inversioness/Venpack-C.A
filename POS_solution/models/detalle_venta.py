# -*- coding: utf-8 -*-
from odoo import api, models, fields
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
        if not data.get('products') and session_ids:
            orders = self.env['pos.order'].search([
                ('state', 'in', ['paid', 'invoiced', 'done']),
                ('session_id', 'in', session_ids)
            ])
            
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

        # ==========================================
        # CONTROL Y ASIGNACIÓN ROBUSTA DE LA TASA
        # ==========================================
        rate = 1.0
        
        # Caso A: Si nos envían los session_ids directamente
        if session_ids:
            # Nos aseguramos de limpiar la lista por si vienen valores falsos
            clean_ids = [s_id for s_id in session_ids if s_id]
            if clean_ids:
                pos_session = self.env['pos.session'].browse(clean_ids)
                if pos_session and hasattr(pos_session[0], 'tax_today') and pos_session[0].tax_today > 0:
                    rate = pos_session[0].tax_today

        # Caso B: Si no vienen session_ids pero vienen config_ids (impresión por Punto de Venta)
        elif config_ids and rate == 1.0:
            # Buscamos la última sesión abierta o cerrada de esa configuración para extraer la tasa
            last_session = self.env['pos.session'].search([
                ('config_id', 'in', config_ids)
            ], order='id desc', limit=1)
            if last_session and hasattr(last_session, 'tax_today') and last_session.tax_today > 0:
                rate = last_session.tax_today

        # Caso C: Respaldo total si sigue en 1.0 (Buscamos la sesión global más reciente que tenga tasa)
        if rate == 1.0:
            last_global_session = self.env['pos.session'].search([
                ('tax_today', '>', 0)
            ], order='id desc', limit=1)
            if last_global_session:
                rate = last_global_session.tax_today

        currency_dif = getattr(self.env.company, 'currency_id_dif', user_currency)

        data.update({
            'total_paid_ref': currency_dif.round(data['total_paid'] / rate) if rate else 0.0,
            'rate_today': rate,
            'symbol_ref': currency_dif.symbol,
            'currency_precision_ref': currency_dif.decimal_places or 2,
        })

        # ==========================================
        # CÁLCULO DE DÓLARES EN PRODUCTOS (Bs / Tasa)
        # ==========================================
        grand_total_usd = 0.0

        if 'products' in data and data['products']:
            for prod in data['products']:
                # Calculamos el total en Bs usando la misma lógica que tu XML
                total_bs = prod.get('quantity', 0.0) * prod.get('price_unit', 0.0)
                
                # Efectuamos la división real por la tasa recuperada
                total_usd = total_bs / rate if rate else 0.0
                prod['total_usd'] = total_usd
                
                grand_total_usd += total_usd

        if 'products_info' in data and isinstance(data['products_info'], dict):
            data['products_info']['total_usd_amount'] = grand_total_usd
        else:
            data['products_info'] = {'total_usd_amount': grand_total_usd}

        return data