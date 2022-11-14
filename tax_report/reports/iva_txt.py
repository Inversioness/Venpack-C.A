from odoo import api, models
import locale
from odoo.exceptions import ValidationError


class IvaTxt(models.AbstractModel):
    _name = 'report.tax_report.iva_txt'
    _description = 'txt de los comprobante de retencion de iva pdf'

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
        docs = self.env['account.move'].browse(docids[0])
        invoice_ids = self.env['account.move'].search([
            ('id', 'in', docids), ('x_ncomprobante', '!=', False)
        ])
        data_txt_iva = []

        for invoice in invoice_ids:

            if invoice.x_tipodoc == 'Factura':
                document_type = '01'
            elif invoice.x_tipodoc == 'Nota de Débito':
                document_type = '02'
            elif invoice.x_tipodoc == 'Nota de Crédito':
                document_type = '03'
            else:
                document_type = ''

            if invoice.reversed_entry_id:
                if invoice.x_tipodoc == 'Nota de Crédito':
                    affected_invoice_no = invoice.reversed_entry_id.ref
                else:
                    affected_invoice_no = invoice.reversed_entry_id.name
            else:
                affected_invoice_no = 0

            rif_company = self.rif_format(invoice.company_id.vat)
            fiscal_period = invoice.date.strftime('%Y%m')
            date = invoice.date
            column_4 = 'C'
            transaction_type = document_type
            rif_supplier = self.rif_format(invoice.fiscal_provider.vat)
            invoice_number = invoice.ref
            control_number = invoice.x_ncontrol
            # amount_total = 0.0
            tax_base = 0.0
            iva_withheld = 0.0
            affected_invoice_number = affected_invoice_no
            voucher_number = invoice.x_ncomprobante #todo campo 13 agregar el xml
            # exempt_amount = 0.0
            # retention_percentage = ''
            column_16 = '0'

            exempt_sum = 0.0
            percentage = ''
            tax_iva = 0.0

            for ili in invoice.invoice_line_ids:
                for ti in ili.tax_ids:
                    if ti.x_tipoimpuesto == 'IVA':
                        tax_base += ili.price_subtotal
                        if tax_iva == 0:
                            line_iva_id = invoice.line_ids.search([('name', '=', ti.name), ('move_id', '=', invoice.id)])
                            tax_iva = abs(line_iva_id[0].amount_currency)
                            percentage = line_iva_id[0].name
                    if ti.x_tipoimpuesto == 'EXENTO':
                        exempt_sum += ili.price_subtotal
                    if ti.x_tipoimpuesto == 'RIVA':
                        line_riva_id = invoice.line_ids.search([('name', '=', ti.name), ('move_id', '=', invoice.id)])
                        iva_withheld = abs(line_riva_id.amount_currency)

            if percentage != '':
                retention_percentage = float(percentage[4:-1])
            else:
                retention_percentage = 0.0

            if invoice.currency_id.name != 'VES':
                tax_base = tax_base * invoice.x_tasa
                exempt_sum = exempt_sum * invoice.x_tasa
                tax_iva = tax_iva * invoice.x_tasa
                iva_withheld = iva_withheld * invoice.x_tasa

            tax_base_format = "{0:.2f}".format(tax_base)

            amount_total = "{0:.2f}".format(tax_iva + tax_base + exempt_sum)

            if exempt_sum == 0.0:
                exempt_amount = 0
            else:
                exempt_amount = "{0:.2f}".format(exempt_sum)

            if iva_withheld == 0.0:
                iva_withheld = 0
            else:
                iva_withheld = "{0:.2f}".format(iva_withheld)


            iva_txt_line = {
                'rif_company': rif_company,
                'fiscal_period': fiscal_period,
                'date': date,
                'column_4': column_4,
                'transaction_type': transaction_type,
                'rif_supplier': rif_supplier,
                'invoice_number': invoice_number,
                'control_number': control_number,
                'amount_total': amount_total,
                'tax_base': tax_base_format,
                'iva_withheld': iva_withheld,
                'affected_invoice_number': affected_invoice_number,
                'voucher_number': voucher_number,
                'exempt_amount': exempt_amount,
                'retention_percentage': retention_percentage,
                'column_16': column_16,
            }
            data_txt_iva.append(iva_txt_line)

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'data_txt_iva': data_txt_iva,
        }
        return docargs
