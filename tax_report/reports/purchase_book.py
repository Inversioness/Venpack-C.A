from odoo import api, models, _
import locale
from odoo.exceptions import ValidationError


class PurchaseBook(models.AbstractModel):
    _name = 'report.tax_report.purchase_book'
    _description = 'Libro de Compras'

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
        invoice_ids = docs.purchase_book_invoice_ids.sorted(key=lambda r: r.invoice_date)

        # if not invoice_ids:
        #     raise ValidationError(
        #         _("No existen documentos para el rango de fechas seleccionadas, que permitan generar el libro de compras"))

        data_purchase_book = []
        number = 0

        sum_amount_total = 0.0
        sum_exempt_amount = 0.0
        sum_tax_base_amount = 0.0
        sum_tax_iva_amount = 0.0
        sum_iva_withheld = 0.0
        total_tax_base_column = 0.0

        if invoice_ids:
            for invoice in invoice_ids:

                number += 1

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

                if invoice.fiscal_provider.x_tipopersona == 'Natural No Domiciliado':
                    type_prov = 'NN'
                elif invoice.fiscal_provider.x_tipopersona == 'Natural Domiciliado':
                    type_prov = 'ND'
                elif invoice.fiscal_provider.x_tipopersona == 'Jurídico No Domiciliado':
                    type_prov = 'JN'
                elif invoice.fiscal_provider.x_tipopersona == 'Jurídico Domiciliado':
                    type_prov = 'JD'
                else:
                    type_prov = ''

                date = invoice.invoice_date.strftime('%d/%m/%Y')
                rif_supplier = self.rif_format(invoice.fiscal_provider.vat)
                provider_name = invoice.fiscal_provider.name
                provider_type = type_prov
                voucher_number = invoice.x_ncomprobante
                import_template_number = invoice.x_nplanilla
                no_proceedings_import = invoice.x_nexpediente
                control_number = invoice.x_ncontrol
                transaction_type = document_type
                affected_invoice_number = affected_invoice_no
                tax_base = 0.0
                tax_iva = 0.0
                iva_withheld = 0.0
                column_17 = '-'

                exempt_sum = 0.0
                percentage = ''
                retention_percentage = 0

                for ili in invoice.invoice_line_ids:
                    for ti in ili.tax_ids:
                        if ti.x_tipoimpuesto == 'IVA':
                            tax_base += ili.price_subtotal
                            if tax_iva == 0:
                                line_iva_id = invoice.line_ids.search([('name', '=', ti.name), ('move_id', '=', invoice.id)])
                                tax_iva = line_iva_id[0].amount_currency
                                percentage = line_iva_id[0].name
                        if ti.x_tipoimpuesto == 'EXENTO':
                            exempt_sum += ili.price_subtotal
                        if ti.x_tipoimpuesto == 'RIVA':
                            line_riva_id = invoice.line_ids.search([('name', '=', ti.name), ('move_id', '=', invoice.id)])
                            iva_withheld = line_riva_id.amount_currency
                            retention_percentage = ti.description[1:-1]

                if percentage != '':
                    iva_percentage = int(percentage[4:-1])
                else:
                    iva_percentage = 0

                if invoice.currency_id.name != 'VES':
                    tax_base = tax_base * invoice.x_tasa # lineas de factura
                    exempt_sum = exempt_sum * invoice.x_tasa # lineas de factura
                    tax_iva = tax_iva * invoice.x_tasa # apunte contable
                    iva_withheld = iva_withheld * invoice.x_tasa # apunte contable

                if invoice.x_tipodoc == 'Nota de Crédito':
                    amount_total = -1 * (abs(tax_iva) + tax_base + exempt_sum)
                    tax_base_amount = -1 * tax_base
                    tax_iva_amount = tax_iva
                    exempt_amount = -1 * exempt_sum
                    iva_withheld_amount = -1 * iva_withheld
                else:
                    amount_total = abs(tax_iva) + tax_base + exempt_sum
                    tax_base_amount = tax_base
                    tax_iva_amount = abs(tax_iva)
                    exempt_amount = exempt_sum
                    iva_withheld_amount = abs(iva_withheld)

                sum_amount_total += amount_total
                sum_exempt_amount += exempt_amount
                sum_tax_base_amount += tax_base_amount
                sum_tax_iva_amount += tax_iva_amount
                sum_iva_withheld += iva_withheld_amount
                total_tax_base_column = sum_tax_base_amount + sum_exempt_amount

                purchase_book_line = {
                    'number': number,
                    'date': date,
                    'rif_supplier': rif_supplier,
                    'provider_name': provider_name,
                    'provider_type': provider_type,
                    'voucher_number': voucher_number,
                    'import_template_number': import_template_number,
                    'no_proceedings_import': no_proceedings_import,
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
                    'retention_percentage': retention_percentage,
                    'iva_withheld': locale.format_string('%10.2f', iva_withheld_amount, grouping=True),
                }
                data_purchase_book.append(purchase_book_line)

        docargs = {
            'doc_ids': docids,
            'doc_model': 'sales.purchase.book',
            'data': data,
            'docs': docs,
            'data_purchase_book': data_purchase_book,
            'sum_amount_total': locale.format_string('%10.2f', sum_amount_total, grouping=True),
            'sum_exempt_amount': locale.format_string('%10.2f', sum_exempt_amount, grouping=True),
            'sum_tax_base_amount': locale.format_string('%10.2f', sum_tax_base_amount, grouping=True),
            'sum_tax_iva_amount': locale.format_string('%10.2f', sum_tax_iva_amount, grouping=True),
            'sum_iva_withheld': locale.format_string('%10.2f', sum_iva_withheld, grouping=True),
            'total_tax_base_column': locale.format_string('%10.2f', total_tax_base_column, grouping=True),
        }
        return docargs
