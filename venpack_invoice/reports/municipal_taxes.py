from odoo import api, models
import locale
from odoo.exceptions import ValidationError


class MunicipalTaxes(models.AbstractModel):
    _name = 'report.venpack_invoice.municipal_taxes'
    _description = 'Impuestos Municipales'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('funcion para obtener datos del cliente para el reporte')
        locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
        docs = self.env['account.move'].browse(docids[0])

        tax_base_impm = 0.0
        code_tax_impm = ''
        percentage_impm = 0
        tax_base = 0.0
        tax_iva = 0.0
        exempt_sum = 0.0
        percentage = ''

        iva_withheld = 0.0

        for ili in docs.invoice_line_ids:
            for ti in ili.tax_ids:
                if ti.x_tipoimpuesto == 'IMPM':
                    tax_base_impm += ili.price_subtotal
                    pos = ti.name.find(' ')
                    code_tax_impm = ti.name[:pos]
                    percentage_impm = abs(ti.amount)

                if ti.x_tipoimpuesto == 'IVA':
                    tax_base += ili.price_subtotal
                    #line_iva_id = docs.line_ids.search([('account_id', '=', ili.account_id.id), ('name', '=', ti.name), ('move_id', '=', docs.id)]) #fix: no sirvio
                    line_iva_id = docs.line_ids.search([('name', '=', ti.name), ('move_id', '=', docs.id)])
                    if len(line_iva_id) > 1:
                        tax_iva = 0.0
                        for lii in line_iva_id:
                            if docs.x_tipodoc == 'Nota de Crédito':
                                tax_iva += lii.credit
                            else:
                                tax_iva += lii.debit
                    else:
                        if docs.x_tipodoc == 'Nota de Crédito':
                            tax_iva = line_iva_id.credit
                        else:
                            tax_iva = line_iva_id.debit
                    percentage = line_iva_id[0].name
                if ti.x_tipoimpuesto == 'EXENTO':
                    exempt_sum += ili.price_subtotal
                if ti.x_tipoimpuesto == 'RIVA':
                    line_riva_id = docs.line_ids.search([('name', '=', ti.name), ('move_id', '=', docs.id)])
                    if docs.x_tipodoc == 'Nota de Crédito':
                        iva_withheld = line_riva_id.debit
                    else:
                        iva_withheld = line_riva_id.credit

        # if docs.currency_id.name == 'USD':
        #     tax_base = tax_base * docs.x_tasa
        #     exempt_sum = exempt_sum * docs.x_tasa

        amount_total = tax_iva + tax_base + exempt_sum

        if percentage != '':
            retention_percentage = percentage[4:]
        else:
            retention_percentage = ''

        #tax_iva = round(tax_base * 0.16, 2)

        if docs.x_tipodoc == 'Factura':
            transaction_type = '01'
        elif docs.x_tipodoc == 'Nota de Crédito':
            transaction_type = '02'
        elif docs.x_tipodoc == 'Nota de Débito':
            transaction_type = '03'
        else:
            transaction_type = ''

        tax_impm_withheld = (tax_base_impm *  percentage_impm) / 100
        amount_impm_paid = tax_base_impm - tax_impm_withheld

        if docs.currency_id.name != 'VES':
            amount_total = amount_total * docs.x_tasa
            tax_base_impm = tax_base_impm * docs.x_tasa
            amount_impm_paid = amount_impm_paid * docs.x_tasa
            tax_impm_withheld = tax_impm_withheld * docs.x_tasa

        if docs.x_tipodoc == 'Nota de Crédito':
            amount_total = -1 * amount_total if amount_total != 0 else amount_total
            tax_base_impm = -1 * tax_base_impm if tax_base_impm != 0 else tax_base_impm
            amount_impm_paid = -1 * amount_impm_paid if amount_impm_paid != 0 else amount_impm_paid
            tax_impm_withheld = -1 * tax_impm_withheld if tax_impm_withheld != 0 else tax_impm_withheld

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'tax_iva': locale.format_string('%10.2f', tax_iva, grouping=True),
            'tax_base': locale.format_string('%10.2f', tax_base, grouping=True),
            'exempt_sum': locale.format_string('%10.2f', exempt_sum, grouping=True),
            'amount_total': locale.format_string('%10.2f', amount_total, grouping=True),
            'tax_base_impm': locale.format_string('%10.2f', tax_base_impm, grouping=True),
            'code_tax_impm': code_tax_impm,
            'percentage_impm': locale.format_string('%10.2f', percentage_impm, grouping=True),
            'tax_impm_withheld': locale.format_string('%10.2f', tax_impm_withheld, grouping=True),
            'amount_impm_paid': locale.format_string('%10.2f', amount_impm_paid, grouping=True),
            'retention_percentage': retention_percentage,
            'iva_withheld': locale.format_string('%10.2f', iva_withheld, grouping=True),
            'transaction_type': transaction_type,
        }
        return docargs
