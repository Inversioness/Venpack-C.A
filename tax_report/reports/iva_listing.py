from odoo import api, models, exceptions, _
import locale
import logging
from datetime import datetime
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class IvaListing(models.AbstractModel):
    _name = 'report.tax_report.iva_listing'
    _description = 'listado de iva pdf'

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
        journal_ids = self.env['account.journal'].search([('x_fiscal', '=', True)])
        if not journal_ids:
            raise exceptions.ValidationError(
                _("No existe registros de diarios contables marcados como fiscales"))

        invoice_ids = self.env['account.move'].search([
            ('id', 'in', docids),('x_ncomprobante', '!=', False), ('journal_id', 'in', journal_ids.ids)
        ]).sorted(key=lambda r: r.x_ncomprobante)

        start_date = invoice_ids[0].date.strftime('%d/%m/%Y')
        final_date = invoice_ids[-1].date.strftime('%d/%m/%Y')

        data_iva_listing = []
        tax_base_total = 0
        tax_iva_total = 0
        iva_withheld_total = 0
        now = datetime.today().strftime('%d/%m/%Y')
        username = self.env.user.name
        for invoice in invoice_ids:
            exempt_sum = 0.0
            tax_base = 0.0
            percentage = ''
            percentage_retencion = ''
            tax_iva = 0.0
            iva_withheld = 0.0
            # amount_total = 0.0
            IVA = False

            for ili in invoice.invoice_line_ids:
                for ti in ili.tax_ids:
                    if ti.x_tipoimpuesto == 'IVA':
                        IVA = True
                        tax_base += ili.price_subtotal
                        if tax_iva == 0:
                            line_iva_id = invoice.line_ids.search([
                                ('name', '=', ti.name), ('move_id', '=', invoice.id)
                            ])
                            tax_iva = abs(line_iva_id[0].amount_currency)
                            percentage = line_iva_id[0].name
                    if ti.x_tipoimpuesto == 'EXENTO':
                        exempt_sum += ili.price_subtotal
                    if ti.x_tipoimpuesto == 'RIVA':
                        IVA = True
                        percentage_retencion = ti.description
                        line_riva_id = invoice.line_ids.search([('name', '=', ti.name), ('move_id', '=', invoice.id)])
                        iva_withheld = abs(line_riva_id.amount_currency)

            if invoice.x_tipodoc == 'Factura':
                document_type = 'FAC'
            elif invoice.x_tipodoc == 'Nota de Crédito':
                document_type = 'NC'
            elif invoice.x_tipodoc == 'Nota de Débito':
                document_type = 'ND'
            else:
                document_type = ''

            if percentage_retencion != '':
                porec_retencion = percentage_retencion[1:]
            else:
                porec_retencion = ''

            amount_total = tax_iva + tax_base + exempt_sum

            if invoice.currency_id.name != 'VES':
                tax_base = tax_base * invoice.x_tasa
                exempt_sum = exempt_sum * invoice.x_tasa
                tax_iva = tax_iva * invoice.x_tasa
                iva_withheld = iva_withheld * invoice.x_tasa

            if invoice.x_tipodoc == 'Nota de Crédito':
                amount_total = -1 * amount_total if amount_total != 0 else amount_total
                tax_base = -1 * tax_base if tax_base != 0 else tax_base
                tax_iva = -1 * tax_iva if tax_iva != 0 else tax_iva
                exempt_sum = -1 * exempt_sum if exempt_sum != 0 else exempt_sum
                iva_withheld = -1 * iva_withheld if iva_withheld != 0 else iva_withheld

            invoice_iva_data = {
                'document_type': document_type,
                'document_number': invoice.ref,
                'date': invoice.date.strftime('%d/%m/%Y'),
                'transaction_number': invoice.x_ncomprobante,
                'provider_name': invoice.fiscal_provider.name,
                'tax_base': locale.format_string('%10.2f', tax_base, grouping=True),
                'tax_iva': locale.format_string('%10.2f', tax_iva, grouping=True),
                'retention_percentage': porec_retencion,
                'th_iva_withheld': locale.format_string('%10.2f', iva_withheld, grouping=True),
            }

            if IVA:
                tax_base_total += tax_base
                tax_iva_total += tax_iva
                iva_withheld_total += iva_withheld
                data_iva_listing.append(invoice_iva_data)

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'fecha': now,
            'username': username,
            'start_date': start_date,
            'final_date': final_date,
            'tax_base_total': locale.format_string('%10.2f', tax_base_total, grouping=True),
            'tax_iva_total': locale.format_string('%10.2f', tax_iva_total, grouping=True),
            'iva_withheld_total': locale.format_string('%10.2f', iva_withheld_total, grouping=True),
            'data_iva_listing': data_iva_listing,
        }

        return docargs
