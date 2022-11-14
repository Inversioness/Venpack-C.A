from odoo import api, models
import locale
from odoo.exceptions import ValidationError


class IvaVoucher(models.AbstractModel):
    _name = 'report.tax_report.iva_voucher'
    _description = 'comprobante de retencion de iva pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('funcion para obtener datos del cliente para el reporte')
        locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
        docs = self.env['account.move'].browse(docids[0])

        fiscal_period = 'Año: ' + str(docs.date.year) + ' / Mes: ' + str(docs.date.month)
        print(fiscal_period)

        exempt_sum = 0.0
        tax_base = 0.0
        percentage = ''
        percentage_retencion = ''
        tax_iva = 0.0
        iva_withheld = 0.0
        #amount_total = 0.0

        for ili in docs.invoice_line_ids:
            for ti in ili.tax_ids:
                if ti.x_tipoimpuesto == 'IVA':
                    tax_base += ili.price_subtotal
                    if tax_iva == 0:
                        line_iva_id = docs.line_ids.search([('name', '=', ti.name), ('move_id', '=', docs.id)])
                        tax_iva = abs(line_iva_id[0].amount_currency)
                        percentage = line_iva_id[0].name
                if ti.x_tipoimpuesto == 'EXENTO':
                    exempt_sum += ili.price_subtotal
                if ti.x_tipoimpuesto == 'RIVA':
                    percentage_retencion = ti.description
                    line_riva_id = docs.line_ids.search([('name', '=', ti.name), ('move_id', '=', docs.id)])
                    iva_withheld = abs(line_riva_id.amount_currency)

        if docs.currency_id.name != 'VES':
            tax_base = tax_base * docs.x_tasa
            exempt_sum = exempt_sum * docs.x_tasa
            tax_iva = tax_iva * docs.x_tasa
            iva_withheld = iva_withheld * docs.x_tasa

        amount_total = tax_iva + tax_base + exempt_sum

        if percentage != '':
            retention_percentage = percentage[4:]
        else:
            retention_percentage = ''

        if percentage_retencion != '':
            porec_retencion = percentage_retencion[1:]
        else:
            porec_retencion = ''

        if docs.x_tipodoc == 'Factura':
            transaction_type = '01'
        elif docs.x_tipodoc == 'Nota de Crédito':
            transaction_type = '02'
        elif docs.x_tipodoc == 'Nota de Débito':
            transaction_type = '03'
        else:
            transaction_type = ''

        if docs.x_tipodoc == 'Nota de Crédito':
            amount_total = -1 * amount_total if amount_total != 0 else amount_total
            tax_base = -1 * tax_base if tax_base != 0 else tax_base
            tax_iva = -1 * tax_iva if tax_iva != 0 else tax_iva
            exempt_sum = -1 * exempt_sum if exempt_sum != 0 else exempt_sum
            iva_withheld = -1 * iva_withheld if iva_withheld != 0 else iva_withheld


        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'porec_retencion': porec_retencion,
            'fiscal_period': fiscal_period,
            'exempt_sum': locale.format_string('%10.2f', exempt_sum, grouping=True),
            'tax_base': locale.format_string('%10.2f', tax_base, grouping=True),
            'retention_percentage': retention_percentage,
            'tax_iva': locale.format_string('%10.2f', tax_iva, grouping=True),
            'iva_withheld': locale.format_string('%10.2f', iva_withheld, grouping=True),
            'amount_total': locale.format_string('%10.2f', amount_total, grouping=True),
            'transaction_type': transaction_type,
        }
        return docargs
