# -*- coding: utf-8 -*-
from odoo import api, models

class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        # 1. Buscamos las órdenes de forma manual
        orders = self.env['pos.order'].search([
            ('state', 'in', ['paid', 'invoiced', 'done']),
            ('session_id', 'in', session_ids)
        ])

        products_sold = {}
        taxes = {}
        for line in orders.mapped('lines'):
            # Agrupar productos
            key = (line.product_id.id, line.price_unit, line.discount)
            if key not in products_sold:
                products_sold[key] = {
                    'product_id': line.product_id.id,
                    'product_name': line.product_id.name,
                    'code': line.product_id.default_code or '',
                    'quantity': 0,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'uom': line.product_uom_id.name,
                    'total_price': 0,
                }
            products_sold[key]['quantity'] += line.qty
            products_sold[key]['total_price'] += line.price_subtotal_incl

            # Agrupar impuestos
            for tax in line.tax_ids_after_fiscal_position:
                if tax.id not in taxes:
                    taxes[tax.id] = {'name': tax.name, 'amount': 0, 'id': tax.id}
                taxes[tax.id]['amount'] += (line.price_subtotal_incl - line.price_subtotal)

        # Agrupar pagos
        payment_details = {}
        for payment in orders.mapped('payment_ids'):
            if payment.payment_method_id.id not in payment_details:
                payment_details[payment.payment_method_id.id] = {
                    'name': payment.payment_method_id.name,
                    'amount': 0,
                }
            payment_details[payment.payment_method_id.id]['amount'] += payment.amount

        # 3. Diccionario de datos final
        data = {
            'total_paid': sum(orders.mapped('amount_total')),
            'payments': list(payment_details.values()),
            'products': list(products_sold.values()),
            'taxes': list(taxes.values()),
            'discount_amount': sum(line.price_unit * line.qty * (line.discount / 100.0) for line in orders.mapped('lines')),
            'taxes_amount': sum(orders.mapped('amount_tax')),
        }

        user_currency = self.env.company.currency_id
        pos_session = self.env['pos.session'].search([('id', 'in', session_ids)], limit=1)
        rate = pos_session.tax_today if pos_session and pos_session.tax_today != 0 else 1.0
        currency_dif = getattr(self.env.company, 'currency_id_dif', user_currency)
        
        if 'currency' not in data: data['currency'] = {}
        data['currency'].update({
            'symbol': user_currency.symbol,
            'position': user_currency.position,
            'decimals': user_currency.decimal_places,
            'precision': user_currency.decimal_places,
            'total_paid': data['total_paid'], 
        })

        data.update({
            'total_paid_ref': currency_dif.round(data['total_paid'] / rate),
            'rate_today': rate,
            'symbol_ref': currency_dif.symbol,
            'currency_precision_ref': currency_dif.decimal_places or 2,
        })

        return data