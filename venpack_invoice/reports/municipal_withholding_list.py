from odoo import api, models
import locale
from odoo.exceptions import ValidationError


class MunicipalWithholdingList(models.AbstractModel):
    _name = 'report.venpack_invoice.municipal_withholding_list'
    _description = 'lista de retenciones municipales'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('funcion para obtener datos del cliente para el reporte')
        locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
        docs = self.env['account.move'].browse(docids[0])
        invoice_ids = self.env['account.move'].search([('id', 'in', docids), ('x_IM_vaucher_number', '!=', False)]).sorted(key=lambda r: (r.x_IM_vaucher_number, r.date))
        start_date = invoice_ids[0].date.strftime('%d/%m/%Y')
        final_date = invoice_ids[-1].date.strftime('%d/%m/%Y')

        data_municipal_listing = []
        tax_base_total = 0
        tax_withheld_total = 0

        for invoice in invoice_ids:
            tax_base_impm = 0.0
            code_tax_impm = ''
            percentage_impm = 0
            IMPM = False

            for ili in invoice.invoice_line_ids:
                for ti in ili.tax_ids:
                    if ti.x_tipoimpuesto == 'IMPM':
                        tax_base_impm += ili.price_subtotal
                        pos = ti.name.find(' ')
                        code_tax_impm = ti.name[:pos]
                        percentage_impm = abs(ti.amount)
                        IMPM = True

            tax_impm_withheld = (tax_base_impm *  percentage_impm) / 100
            amount_impm_paid = tax_base_impm - tax_impm_withheld

            if invoice.currency_id.name != 'VES':
                tax_base_impm = tax_base_impm * invoice.x_tasa
                tax_impm_withheld = tax_impm_withheld * invoice.x_tasa
                amount_impm_paid = amount_impm_paid * invoice.x_tasa

            if invoice.x_tipodoc == 'Nota de Crédito':
                # amount_total = -1 * amount_total if amount_total != 0 else amount_total
                tax_base_impm = -1 * tax_base_impm if tax_base_impm != 0 else tax_base_impm
                amount_impm_paid = -1 * amount_impm_paid if amount_impm_paid != 0 else amount_impm_paid
                tax_impm_withheld = -1 * tax_impm_withheld if tax_impm_withheld != 0 else tax_impm_withheld

            tax_base_total += tax_base_impm
            tax_withheld_total += tax_impm_withheld

            invoice_municipal_data = {
                "provider": invoice.partner_id.vat,
                "provider_name": invoice.partner_id.name,
                "retention_code": code_tax_impm,
                "retention_number": invoice.x_IM_vaucher_number,
                "affected_invoice": invoice.ref,
                "control_number": invoice.x_ncontrol,
                "date": invoice.date,
                "retention_percentage": locale.format_string('%10.2f', percentage_impm, grouping=True),
                "tax_base": locale.format_string('%10.2f', tax_base_impm, grouping=True),
                "tax_withheld": locale.format_string('%10.2f', tax_impm_withheld, grouping=True),
            }

            if IMPM:
                data_municipal_listing.append(invoice_municipal_data)

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'start_date': start_date,
            'final_date': final_date,
            'data_municipal_listing': data_municipal_listing,
            'tax_base_total': locale.format_string('%10.2f', tax_base_total, grouping=True),
            'tax_withheld_total': locale.format_string('%10.2f', tax_withheld_total, grouping=True),
        }
        return docargs
