from odoo import api, models, _
import locale
import logging
from datetime import datetime
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class IslrListing(models.AbstractModel):
    _inherit = 'report.tax_report.islr_listing'
    _description = 'Mofificar listado de islr pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('funcion para obtener datos del cliente para el reporte')
        locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
        docs = self.env['account.move'].browse(docids[0])
        invoice_ids = self.env['account.move'].search([('id', 'in', docids), ('x_comp_isl', '!=', False)]).sorted(key=lambda r: (r.x_comp_isl, r.date))
        start_date = invoice_ids[0].date.strftime('%d/%m/%Y')
        final_date = invoice_ids[-1].date.strftime('%d/%m/%Y')

        data_islr_listing = []
        tax_base_total = 0
        tax_withheld_total = 0
        now = datetime.today().strftime('%d/%m/%Y')
        username = self.env.user.name
        for invoice in invoice_ids:
            invoice_line_group_by_name_tax = self.transform_and_group_by_item(data=invoice.invoice_line_ids, item_group="tax_ids", sub_item_group='x_tipoimpuesto')
            if invoice_line_group_by_name_tax:
                for key, value in invoice_line_group_by_name_tax.items():
                    tax_withheld = 0.0
                    price_subtotal = 0
                    line_id = invoice.line_ids.search([('name', '=', key), ('move_id', '=', invoice.id)])
                    # tax_withheld_line = abs(line_id.amount_currency)
                    tax_withheld += abs(line_id.amount_currency)
                    account_tax_id = self.env['account.tax'].search([('name', '=', key)])
                    retention_code = str(account_tax_id.x_conceptoret)
                    retention_number = key[:6]
                    retention_percentage = locale.format_string('%10.2f', account_tax_id.amount, grouping=True).replace("-", "")

                    for ili in value:
                        price_subtotal += ili.price_subtotal

                    if invoice.currency_id.name != 'VES':
                        price_subtotal = price_subtotal * invoice.x_tasa
                        tax_withheld = tax_withheld * invoice.x_tasa

                    if invoice.x_tipodoc == 'Nota de Crédito':
                        price_subtotal = -1 * price_subtotal if price_subtotal != 0 else price_subtotal
                        tax_withheld = -1 * tax_withheld if tax_withheld != 0 else tax_withheld

                    tax_base_total += price_subtotal
                    tax_withheld_total += tax_withheld

                    amount_price_subtotal = locale.format_string('%10.2f', price_subtotal, grouping=True)

                    date = invoice.date.strftime('%d/%m/%Y')
                    rif_supplier = self.rif_format(invoice.fiscal_provider.vat)
                    provider_name = invoice.fiscal_provider.name
                    if invoice.x_tipodoc == 'Factura':
                        document_type = 'FAC'
                    elif invoice.x_tipodoc == 'Nota de Crédito':
                        document_type = 'NC'
                    elif invoice.x_tipodoc == 'Nota de Débito':
                        document_type = 'ND'
                    else:
                        document_type = ''

                    invoice_islr_data = {
                        'provider': rif_supplier,
                        'provider_name': provider_name,
                        'retention_code': retention_code,
                        'retention_number': invoice.x_comp_isl,
                        'document_type': document_type,
                        'document': invoice.ref,
                        'control_number': invoice.x_ncontrol,
                        'retention_date': date,
                        'retention_percentage': retention_percentage,
                        'tax_base': amount_price_subtotal,
                        'tax_withheld': locale.format_string('%10.2f', tax_withheld, grouping=True)
                    }
                    data_islr_listing.append(invoice_islr_data)

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
            'tax_withheld_total': locale.format_string('%10.2f', tax_withheld_total, grouping=True),
            'data_islr_listing': data_islr_listing,
        }
        return docargs
