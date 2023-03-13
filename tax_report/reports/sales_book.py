from odoo import api, models, _
from datetime import datetime
import locale
import json
from odoo.exceptions import ValidationError


class SalesBook(models.AbstractModel):
    _name = 'report.tax_report.sales_book'
    _description = 'Libro de Ventas'

    @staticmethod
    def rif_format(rif):
        characters = "-./_ "
        for x in range(len(characters)):
            rif = rif.replace(characters[x], "")
        return rif

    @api.model
    def _get_report_values(self, docids, data=None):
        print('funcion para obtener datos del cliente para el reporte')
        locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
        docs = self.env['sales.purchase.book'].browse(docids[0])
        invoice_ids = docs.sales_book_invoice_ids.sorted(key=lambda r: (r.invoice_date, r.ref))

        # if not invoice_ids:
        #     raise ValidationError(
        #         _("No existen documentos para el rango de fechas seleccionadas, que permitan generar el libro de ventas"))

        data_sales_book = []
        number = 0

        sum_amount_total = 0.0
        sum_exempt_amount = 0.0
        sum_tax_base_amount = 0.0
        sum_tax_iva_amount = 0.0
        sum_iva_withheld = 0.0
        total_tax_base_column = 0.0

        if invoice_ids:
            for invoice in invoice_ids:
                flag = False
                number += 1
                date = invoice.date.strftime('%d/%m/%Y')
                rif_supplier = self.rif_format(invoice.fiscal_provider.vat) if invoice.fiscal_provider.vat else ""
                customer_name = invoice.fiscal_provider.name
                control_number = invoice.x_ncontrol

                tax_base = 0.0
                tax_iva = 0.0
                iva_withheld = 0.0
                column_17 = '-'

                exempt_sum = 0.0
                percentage = ''

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

                if percentage != '':
                    iva_percentage = int(percentage[4:-1])
                else:
                    iva_percentage = 0

                # para calculo de retencion
                payment_date = ''
                if invoice.invoice_payments_widget != 'false':
                    res = json.loads(invoice.invoice_payments_widget)
                    for apr in res['content']:
                        memo = apr['ref']
                        type_journal = memo[0:3]
                        if type_journal == 'IVA':
                            account_payment = self.env['account.payment'].search([('id', '=', apr['account_payment_id'])])
                            payment_date = account_payment.document_date if account_payment.document_date else account_payment.date
                            # payment_date = datetime.strptime(apr['date'], '%Y-%m-%d').date()
                            # if docs.start_date <= payment_date <= docs.final_date:
                            if docs.start_date <= account_payment.date <= docs.final_date:
                                # print('verdadero', payment_date)
                                flag = True
                                # ref_journal = memo[memo.find('(') + 1:-1]
                                # account_payment = self.env['account.payment'].search([
                                #     ('move_id', '=', apr['move_id']),
                                #     ('ref', '=', ref_journal),
                                # ])
                                # iva_withheld = apr[
                                #                    'amount'] * account_payment.x_tasa if invoice.currency_id.name != 'VES' else \
                                # apr['amount']
                                iva_withheld = account_payment.amount * account_payment.x_tasa if invoice.currency_id.name != 'VES' else \
                                    account_payment.amount
                                iva_receipt_number = account_payment.ref
                                break
                            else:
                                iva_withheld = 0.0
                                iva_receipt_number = ""
                                break
                        else:
                            iva_withheld = 0.0
                            iva_receipt_number = ""
                else:
                    iva_withheld = 0.0
                    iva_receipt_number = ""

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

                # calculo del porcentaje de retencion
                if tax_iva_amount == 0.0:
                    retention_percentage = ''
                elif iva_withheld_amount == 0.0:
                    retention_percentage = ''
                elif round(iva_withheld_amount, 2) == round(tax_iva_amount, 2):
                    retention_percentage = '100'
                else:
                    retention_percentage = '75'

                if docs.start_date <= invoice.date <= docs.final_date:
                    if invoice.x_tipodoc == 'Factura':
                        document_type = '01'
                        invoice_number = invoice.ref
                        debit_note = ''
                        credit_note = ''
                    elif invoice.x_tipodoc == 'Nota de Crédito':
                        document_type = '02'
                        invoice_number = ''
                        debit_note = ''
                        credit_note = invoice.ref
                    elif invoice.x_tipodoc == 'Nota de Débito':
                        document_type = '03'
                        invoice_number = ''
                        debit_note = invoice.ref
                        credit_note = ''
                    else:
                        document_type = ''


                    if invoice.reversed_entry_id:
                        affected_invoice_no = invoice.reversed_entry_id.ref
                    else:
                        affected_invoice_no = ''

                    transaction_type = document_type
                    affected_invoice_number = affected_invoice_no

                    sum_amount_total += amount_total
                    sum_exempt_amount += exempt_amount
                    sum_tax_base_amount += tax_base_amount
                    sum_tax_iva_amount += tax_iva_amount
                    sum_iva_withheld += iva_withheld_amount
                    total_tax_base_column = sum_tax_base_amount + sum_exempt_amount

                    sales_book_line = {
                        'number': number,
                        'date': date,
                        'rif_supplier': rif_supplier,
                        'customer_name': customer_name,
                        'invoice_number': invoice_number,
                        'control_number': control_number,
                        'debit_note': debit_note,
                        'credit_note': credit_note,
                        'transaction_type': transaction_type,
                        'affected_invoice_number': affected_invoice_number,
                        'amount_total': locale.format_string('%10.2f', amount_total, grouping=True),
                        'exempt_amount': locale.format_string('%10.2f', exempt_amount, grouping=True),
                        'tax_base': locale.format_string('%10.2f', tax_base_amount, grouping=True),
                        'iva_percentage': iva_percentage,
                        'tax_iva': locale.format_string('%10.2f', tax_iva_amount, grouping=True),
                        'retention_percentage': '',
                        'iva_withheld': locale.format_string('%10.2f', 0.00, grouping=True),
                        'iva_receipt_number': '',
                    }
                    data_sales_book.append(sales_book_line)

                    if flag:
                        sales_book_line_retention = sales_book_line.copy()
                        number += 1
                        vals = {
                            'number': number,
                            'date': payment_date.strftime('%d/%m/%Y'),
                            'invoice_number': invoice_number,
                            'transaction_type': '01',
                            'affected_invoice_number': '',
                            'amount_total': locale.format_string('%10.2f', 0.00, grouping=True),
                            'exempt_amount': locale.format_string('%10.2f', 0.00, grouping=True),
                            'tax_base': locale.format_string('%10.2f', 0.00, grouping=True),
                            'iva_percentage': '',
                            'tax_iva': locale.format_string('%10.2f', 0.00, grouping=True),
                            'retention_percentage': retention_percentage,
                            'iva_withheld': locale.format_string('%10.2f', iva_withheld_amount, grouping=True),
                            'iva_receipt_number': iva_receipt_number,
                        }
                        sales_book_line_retention.update(vals)
                        data_sales_book.append(sales_book_line_retention)

                else:
                    document_type = '04'
                    invoice_number = invoice.ref
                    debit_note = ''
                    credit_note = ''

                    # sum_amount_total += amount_total
                    # sum_exempt_amount += exempt_amount
                    # sum_tax_base_amount += tax_base_amount
                    # sum_tax_iva_amount += tax_iva_amount
                    sum_iva_withheld += iva_withheld_amount
                    # total_tax_base_column = sum_tax_base_amount + sum_exempt_amount

                    sales_book_line = {
                        'number': number,
                        'date': payment_date.strftime('%d/%m/%Y'),
                        'rif_supplier': rif_supplier,
                        'customer_name': customer_name,
                        'invoice_number': invoice_number,
                        'control_number': control_number,
                        'debit_note': debit_note,
                        'credit_note': credit_note,
                        'transaction_type': document_type,
                        'affected_invoice_number': '',
                        'amount_total': locale.format_string('%10.2f', 0.00, grouping=True),
                        'exempt_amount': locale.format_string('%10.2f', 0.00, grouping=True),
                        'tax_base': locale.format_string('%10.2f', 0.00, grouping=True),
                        'iva_percentage': '',
                        'tax_iva': locale.format_string('%10.2f', 0.00, grouping=True),
                        'retention_percentage': retention_percentage,
                        'iva_withheld': locale.format_string('%10.2f', iva_withheld_amount, grouping=True),
                        'iva_receipt_number': iva_receipt_number,
                    }

                    data_sales_book.append(sales_book_line)


        docargs = {
            'doc_ids': docids,
            'doc_model': 'sales.purchase.book',
            'data': data,
            'docs': docs,
            'data_sales_book': sorted(data_sales_book, key=lambda x: x['date']),
            'sum_amount_total': locale.format_string('%10.2f', sum_amount_total, grouping=True),
            'sum_exempt_amount': locale.format_string('%10.2f', sum_exempt_amount, grouping=True),
            'sum_tax_base_amount': locale.format_string('%10.2f', sum_tax_base_amount, grouping=True),
            'sum_tax_iva_amount': locale.format_string('%10.2f', sum_tax_iva_amount, grouping=True),
            'sum_iva_withheld': locale.format_string('%10.2f', sum_iva_withheld, grouping=True),
            'total_tax_base_column': locale.format_string('%10.2f', total_tax_base_column, grouping=True),
        }
        return docargs
