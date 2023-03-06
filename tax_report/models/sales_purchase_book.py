# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
import locale
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


def get_years():
    year_list = []
    for i in range(2016, 2036):
        year_list.append((str(i), str(i)))
    return year_list


class SalesPurchaseBook(models.Model):
    _name = 'sales.purchase.book'
    _description = "Modelo para definir el libro de ventas y compras"

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)
    month = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                             ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                             ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')],
                             string='Mes')
    year = fields.Selection(get_years(), string='Año')
    start_date = fields.Date(string="Fecha de Inicio")
    final_date = fields.Date(string="Fecha de Final")
    last_excess_tax_credits = fields.Float(string="Excedentes de Creditos Fiscales del Mes Anterior")
    accumulated_withholdings_deducted = fields.Float(string="Retenciones Acumuladas por Descontar")
    # fiscal_period_type = fields.Char(string='Periodo Fiscal', readonly=True, default=lambda self: self.env['ir.config_parameter'].sudo().get_param('tax_report.fiscal_period_type'))

    # Libro de Ventas
    sales_book_invoice_ids = fields.Many2many(
        'account.move',
        'sales_book_account_move_rel',
        'sales_purchase_book_id',
        'account_move_id',
        string='Facturas del libro de ventas'
    )
    sale_sum_amount_total = fields.Float(string='Total Ventas (Incluye IVA)')
    sale_sum_exempt_amount = fields.Float(string='Ventas Internas No Gravadas')
    sale_sum_tax_base_amount = fields.Float(string='Base Imponible')
    sale_sum_tax_iva_amount = fields.Float(string='Impuesto IVA')
    sale_sum_iva_withheld = fields.Float(string='Iva Retenido (por el comprador)')

    # Libro de Compras
    purchase_book_invoice_ids = fields.Many2many(
        'account.move',
        'purchase_book_account_move_rel',
        'sales_purchase_book_id',
        'account_move_id',
        string='Facturas del libro de ventas'
    )
    purchase_sum_amount_total = fields.Float(string='Total Compras (Incluye IVA)')
    purchase_sum_exempt_amount = fields.Float(string='Compras sin Derecho a IVA')
    purchase_sum_tax_base_amount = fields.Float(string='Base Imponible')
    purchase_sum_tax_iva_amount = fields.Float(string='Impuesto IVA')
    purchase_sum_iva_withheld = fields.Float(string='Iva Retenido al Vendedor')

    @staticmethod
    def rif_format(rif):
        characters = "-./_ "
        for x in range(len(characters)):
            rif = rif.replace(characters[x], "")
        return rif

    @staticmethod
    def date_range(month, year):
        start_date = datetime.datetime.strptime('1-' + month + '-' + year, '%d-%m-%Y')
        end_date = ''

        if int(month) == 12:
            end_date_aux = datetime.datetime.strptime('1-' + '1' + '-' + str(int(year) + 1), '%d-%m-%Y')
            end_date = end_date_aux - datetime.timedelta(seconds=1)
        else:
            end_date_aux = datetime.datetime.strptime('1-' + str(int(month) + 1) + '-' + year,
                                                      '%d-%m-%Y')
            end_date = end_date_aux - datetime.timedelta(seconds=1)

        return start_date, end_date

    def generate_sales_book(self, invoice_ids, start_date, end_date):
        sum_amount_total = 0.0
        sum_exempt_amount = 0.0
        sum_tax_base_amount = 0.0
        sum_tax_iva_amount = 0.0
        sum_iva_withheld = 0.0
        total_tax_base_column = 0.0
        invoices = []


        if invoice_ids:
            invoices_ids_by_date = invoice_ids.sorted(key=lambda r: (r.date, r.ref))
            for invoice in invoices_ids_by_date:
                tax_base = 0.0
                tax_iva = 0.0
                iva_withheld = 0.0
                exempt_sum = 0.0

                for ili in invoice.invoice_line_ids:
                    for ti in ili.tax_ids:
                        if ti.x_tipoimpuesto == 'IVA':
                            tax_base += ili.price_subtotal
                            if tax_iva == 0:
                                line_iva_id = invoice.line_ids.search(
                                    [('name', '=', ti.name), ('move_id', '=', invoice.id)])
                                tax_iva = line_iva_id[0].amount_currency
                        if ti.x_tipoimpuesto == 'EXENTO':
                            exempt_sum += ili.price_subtotal

                # para calculo de retencion
                payment_date = ''
                if invoice.invoice_payments_widget != 'false':
                    res = json.loads(invoice.invoice_payments_widget)
                    for apr in res['content']:
                        memo = apr['ref']
                        type_journal = memo[0:3]
                        if type_journal == 'IVA':
                            payment_date = datetime.strptime(apr['date'], '%Y-%m-%d').date()
                            if start_date <= payment_date <= end_date:
                                ref_journal = memo[memo.find('(') + 1:-1]
                                account_payment = self.env['account.payment'].search([
                                    ('move_id', '=', apr['move_id']),
                                    ('ref', '=', ref_journal),
                                ])
                                iva_withheld = apr[
                                                   'amount'] * account_payment.x_tasa if invoice.currency_id.name != 'VES' else \
                                    apr['amount']
                                iva_receipt_number = account_payment.ref
                                break
                            else:
                                iva_withheld = 0.0
                                break
                        else:
                            iva_withheld = 0.0
                else:
                    iva_withheld = 0.0

                if invoice.currency_id.name != 'VES':
                    tax_base = tax_base * invoice.x_tasa  # lineas de factura
                    exempt_sum = exempt_sum * invoice.x_tasa  # lineas de factura
                    tax_iva = tax_iva * invoice.x_tasa  # apunte contable
                    # iva_withheld = iva_withheld * invoice.x_tasa  # lineas de factura

                if invoice.x_tipodoc == 'Nota de Crédito':
                    amount_total = -1 * (abs(tax_iva) + tax_base + exempt_sum)
                    tax_base_amount = -1 * tax_base if tax_base != 0.0 else tax_base
                    tax_iva_amount = -1 * abs(tax_iva) if tax_iva != 0.0 else tax_iva
                    exempt_amount = -1 * exempt_sum if exempt_sum != 0.0 else exempt_sum
                    iva_withheld_amount = -1 * iva_withheld if iva_withheld != 0.0 else iva_withheld
                else:
                    amount_total = abs(tax_iva) + tax_base + exempt_sum
                    tax_base_amount = tax_base
                    tax_iva_amount = abs(tax_iva)
                    exempt_amount = exempt_sum
                    iva_withheld_amount = iva_withheld

                invoices.append(invoice.id)

                if start_date <= invoice.date <= end_date:
                    sum_amount_total += amount_total
                    sum_exempt_amount += exempt_amount
                    sum_tax_base_amount += tax_base_amount
                    sum_tax_iva_amount += tax_iva_amount
                    sum_iva_withheld += iva_withheld_amount
                    total_tax_base_column = sum_tax_base_amount + sum_exempt_amount

                else:
                    sum_iva_withheld += iva_withheld_amount



        # sum_amount_total = 0.0
        # sum_exempt_amount = 0.0
        # sum_tax_base_amount = 0.0
        # sum_tax_iva_amount = 0.0
        # sum_iva_withheld = 0.0
        # invoices = []
        #
        # invoices_ids_by_date = invoice_ids.sorted(key=lambda r: (r.date, r.ref))
        #
        # for invoice in invoices_ids_by_date:
        #     tax_base = 0.0
        #     tax_iva = 0.0
        #     exempt_sum = 0.0
        #     iva_withheld = 0.0
        #
        #     for ili in invoice.invoice_line_ids:
        #         for ti in ili.tax_ids:
        #             if ti.x_tipoimpuesto == 'IVA':
        #                 tax_base += ili.price_subtotal
        #                 if tax_iva == 0:
        #                     line_iva_id = invoice.line_ids.search([('name', '=', ti.name), ('move_id', '=', invoice.id)])
        #                     tax_iva = line_iva_id[0].amount_currency
        #                     percentage = line_iva_id[0].name
        #             if ti.x_tipoimpuesto == 'EXENTO':
        #                 exempt_sum += ili.price_subtotal
        #
        #
        #     if invoice.invoice_payments_widget != 'false':
        #         res = json.loads(invoice.invoice_payments_widget)
        #         for apr in res['content']:
        #             memo = apr['ref']
        #             type_journal = memo[0:3]
        #
        #             if type_journal == 'IVA':
        #                 ref_journal = memo[memo.find('(') + 1:-1]
        #                 account_payment = self.env['account.payment'].search([
        #                     ('move_id', '=', apr['move_id']),
        #                     ('ref', '=', ref_journal),
        #                 ])
        #                 iva_withheld = apr['amount'] * account_payment.x_tasa if invoice.currency_id.name != 'VES' else apr['amount']
        #                 break
        #             else:
        #                 iva_withheld = 0.0
        #     else:
        #         iva_withheld = 0.0
        #
        #     if invoice.currency_id.name != 'VES':
        #         tax_base = tax_base * invoice.x_tasa  # lineas de factura
        #         exempt_sum = exempt_sum * invoice.x_tasa  # lineas de factura
        #         tax_iva = tax_iva * invoice.x_tasa  # apunte contable
        #         iva_withheld = iva_withheld * invoice.x_tasa  # lineas de factura
        #
        #     if invoice.x_tipodoc == 'Nota de Crédito':
        #         amount_total = -1 * (abs(tax_iva) + tax_base + exempt_sum)
        #         tax_base_amount = -1 * tax_base if tax_base != 0.0 else tax_base
        #         tax_iva_amount = -1 * abs(tax_iva) if tax_iva != 0.0 else tax_iva
        #         exempt_amount = -1 * exempt_sum if exempt_sum != 0.0 else exempt_sum
        #         iva_withheld_amount = -1 * iva_withheld if iva_withheld != 0.0 else iva_withheld
        #     else:
        #         amount_total = abs(tax_iva) + tax_base + exempt_sum
        #         tax_base_amount = tax_base
        #         tax_iva_amount = abs(tax_iva)
        #         exempt_amount = exempt_sum
        #         iva_withheld_amount = iva_withheld
        #
        #     invoices.append(invoice.id)
        #
        #     # verificar si el docuemnto se encuentra dentro de la fecha seleccionada.
        #     if start_date <= invoice.date <= end_date:
        #         sum_amount_total += amount_total
        #         sum_exempt_amount += exempt_amount
        #         sum_tax_base_amount += tax_base_amount
        #         sum_tax_iva_amount += tax_iva_amount
        #         sum_iva_withheld += iva_withheld
        #     else:
        #         sum_iva_withheld += iva_withheld

        vals = {
            'sale_sum_amount_total': round(sum_amount_total, 2),
            'sale_sum_exempt_amount': round(sum_exempt_amount, 2),
            'sale_sum_tax_base_amount': round(sum_tax_base_amount, 2),
            'sale_sum_tax_iva_amount': round(sum_tax_iva_amount, 2),
            'sale_sum_iva_withheld': round(sum_iva_withheld, 2),
            'sales_book_invoice_ids': [(6, 0, invoices)]
        }
        return vals

    def generate_purchase_book(self, invoice_ids):
        sum_amount_total = 0.0
        sum_exempt_amount = 0.0
        sum_tax_base_amount = 0.0
        sum_tax_iva_amount = 0.0
        sum_iva_withheld = 0.0
        invoices = []
        for invoice in invoice_ids:
            tax_base = 0.0
            tax_iva = 0.0
            iva_withheld = 0.0
            exempt_sum = 0.0

            for ili in invoice.invoice_line_ids:
                for ti in ili.tax_ids:
                    if ti.x_tipoimpuesto == 'IVA':
                        tax_base += ili.price_subtotal
                        if tax_iva == 0:
                            line_iva_id = invoice.line_ids.search(
                                [('name', '=', ti.name), ('move_id', '=', invoice.id)])
                            tax_iva = line_iva_id[0].amount_currency
                            percentage = line_iva_id[0].name
                    if ti.x_tipoimpuesto == 'EXENTO':
                        exempt_sum += ili.price_subtotal
                    if ti.x_tipoimpuesto == 'RIVA':
                        line_riva_id = invoice.line_ids.search([('name', '=', ti.name), ('move_id', '=', invoice.id)])
                        iva_withheld = line_riva_id.amount_currency

            if invoice.currency_id.name != 'VES':
                tax_base = tax_base * invoice.x_tasa  # lineas de factura
                exempt_sum = exempt_sum * invoice.x_tasa  # lineas de factura
                tax_iva = tax_iva * invoice.x_tasa  # apunte contable
                iva_withheld = iva_withheld * invoice.x_tasa  # apunte contable

            if invoice.x_tipodoc == 'Nota de Crédito':
                amount_total = -1 * (abs(tax_iva) + tax_base + exempt_sum)
                tax_base_amount = -1 * tax_base
                tax_iva_amount = tax_iva
                exempt_amount = -1 * exempt_sum
                iva_withheld_amount = iva_withheld
            else:
                amount_total = abs(tax_iva) + tax_base + exempt_sum
                tax_base_amount = tax_base
                tax_iva_amount = abs(tax_iva)
                exempt_amount = exempt_sum
                iva_withheld_amount = abs(iva_withheld)

            invoices.append(invoice.id)

            sum_amount_total += amount_total
            sum_exempt_amount += exempt_amount
            sum_tax_base_amount += tax_base_amount
            sum_tax_iva_amount += tax_iva_amount
            sum_iva_withheld += iva_withheld_amount

        vals = {
            'purchase_sum_amount_total': round(sum_amount_total, 2),
            'purchase_sum_exempt_amount': round(sum_exempt_amount, 2),
            'purchase_sum_tax_base_amount': round(sum_tax_base_amount, 2),
            'purchase_sum_tax_iva_amount': round(sum_tax_iva_amount, 2),
            'purchase_sum_iva_withheld': round(sum_iva_withheld, 2),
            'purchase_book_invoice_ids': [(6, 0, invoices)]
        }
        return vals

    def generate_data(self, start_date, end_date, create_res):
        fiscal_journal_ids = self.env['account.journal'].search([('x_fiscal', '=', True)])

        payment_ids = self.env['account.payment'].search([
            ('date', '>=', start_date), ('date', '<=', end_date),
            ('journal_id.tax_code', '=', 'RIVA')
        ])

        move_ids = []
        for pi in payment_ids:
            move_ids.extend([element for element in pi.reconciled_invoice_ids.ids if element not in move_ids])

        sales_book_invoice_2 = self.env['account.move'].search([
            ('id', 'in', move_ids),
            ('journal_id', 'in', fiscal_journal_ids.ids), ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund'])
        ], order="invoice_date ASC")

        sales_book_invoice = self.env['account.move'].search([
            ('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date),
            ('journal_id', 'in', fiscal_journal_ids.ids), ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund'])
        ], order="invoice_date ASC")

        sales_book_invoice |= sales_book_invoice_2

        purchase_book_invoice = self.env['account.move'].search([
            ('date', '>=', start_date), ('date', '<=', end_date),
            ('journal_id', 'in', fiscal_journal_ids.ids), ('state', '=', 'posted'),
            ('move_type', 'in', ['in_invoice', 'in_refund'])
        ], order="invoice_date ASC")

        if sales_book_invoice:
            sale_boook_data = self.generate_sales_book(sales_book_invoice, start_date, end_date)
            create_res.write(sale_boook_data)

        if purchase_book_invoice:
            purchase_boook_data = self.generate_purchase_book(purchase_book_invoice)
            create_res.write(purchase_boook_data)


    @api.model
    def create(self, vals):
        fiscal_period_type = 'date' #TODO falta terminar lo de la varible de configuracion month
        if fiscal_period_type == 'month':
            # validar que no exista un registro con el mismo periodos fiscal
            sales_purchase_book_id = self.env['sales.purchase.book'].search([
                ('month', '=', vals['month']), ('year', '=', vals['year'])
            ])
            if not sales_purchase_book_id:
                create_res = super().create(vals)
                # fiscal_period_type = self.env['ir.config_parameter'].sudo().get_param('tax_report.fiscal_period_type')

                now = datetime.datetime.utcnow()

                if int(create_res.year) > now.year:
                    raise exceptions.UserError('Periodo fiscal aun no disponible, seleccione otro año')
                else:
                    if int(create_res.month) >= now.month:
                        raise exceptions.UserError('Periodo fiscal aun no disponible, seleccione otro mes')
                    else:
                        # definir rango de fecha para el mes seleccionado
                        start_date, end_date = self.date_range(create_res.month, create_res.year)
                        vals = {
                            'start_date': start_date,
                            'final_date': end_date
                        }
                        create_res.write(vals)

                        self.generate_data(start_date, end_date, create_res)

            else:
                raise exceptions.UserError('Ya existe un registro para el periodo fiscal seleccionado.')
        elif fiscal_period_type == 'date':
            create_res = super().create(vals)
            start_date = create_res.start_date
            end_date = create_res.final_date
            self.generate_data(start_date, end_date, create_res)

        return create_res





