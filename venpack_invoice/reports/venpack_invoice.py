from odoo import api, models
import locale
from odoo.exceptions import ValidationError


class PalmaSuitesInvoice(models.AbstractModel):
    _name = 'report.venpack_invoice.custom_invoice'
    _description = 'Factura de Inversiones Venpack pdf'

    @staticmethod
    def description_format(name):
        characters = "]"
        index = name.find(characters)
        if index != -1:
            description = name[index + 1:]
        else:
            description = name
        return description

    @api.model
    def _get_report_values(self, docids, data=None):
        print('funcion para obtener datos del cliente para el reporte')
        locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
        docs = self.env['account.move'].browse(docids[0])

        amount_untaxed = 0.0
        exempt_sum = 0.0
        tax_base = 0.0
        percentage = ''
        tax_iva = 0.0
        iva_withheld = 0.0
        amount_total = 0.0
        discount_sum = 0.0

        street = docs.partner_id.street if docs.partner_id.street else ''
        street2 = docs.partner_id.street2 if docs.partner_id.street2 else ''
        zip_code = docs.partner_id.zip if docs.partner_id.zip else ''
        address = street + ' ' + street2  + ' ' + zip_code
        lines = []
        for ili in docs.invoice_line_ids:
            vals = {
                'price_subtotal': ili.price_subtotal,
                'price_subtotal_2': locale.format_string(' % 10.2f', ili.price_subtotal, grouping=True),
                'price_total': ili.price_total,
                'price_total_2': locale.format_string('%10.2f', ili.price_total, grouping=True),
                'default_code': ili.product_id.default_code,
                'name': self.description_format(ili.name),
                'quantity': locale.format_string('%10.2f', ili.quantity,  grouping=True),
                'product_uom_id': ili.product_uom_id.name,
                'price_unit': ili.price_unit,
                'price_unit_2': locale.format_string('%10.2f', ili.price_unit, grouping=True),
                'discount': ili.discount,
                'display_type': ili.display_type
            }
            lines.append(vals)
            for ti in ili.tax_ids:
                if ili.discount:
                    discount_sum += round(ili.price_unit * (ili.discount / 100), 2)
                else:
                    discount_sum += 0.0

                amount_untaxed += ili.unit_price_without_tax
                if ti.x_tipoimpuesto == 'IVA':
                    tax_base += ili.price_subtotal
                    line_iva_id = docs.line_ids.search([('name', '=', ti.name), ('move_id', '=', docs.id)])
                    if docs.x_tipodoc == 'Nota de Crédito':
                        tax_iva = line_iva_id.debit
                    else:
                        tax_iva = line_iva_id.credit
                    percentage = line_iva_id.name
                if ti.x_tipoimpuesto == 'EXENTO':
                    exempt_sum += ili.price_subtotal
                if ti.x_tipoimpuesto == 'RIVA':
                    line_riva_id = docs.line_ids.search([('name', '=', ti.name), ('move_id', '=', docs.id)])
                    if docs.x_tipodoc == 'Nota de Crédito':
                        iva_withheld = line_riva_id.debit
                    else:
                        iva_withheld = line_riva_id.credit

        amount_total = tax_iva + tax_base + exempt_sum

        if percentage != '':
            retention_percentage = percentage[4:]
        else:
            retention_percentage = ''


        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'amount_untaxed': locale.format_string('%10.2f', docs.amount_untaxed, grouping=True),
            'discount_sum': locale.format_string('%10.2f', discount_sum, grouping=True),
            'tax_iva': locale.format_string('%10.2f', tax_iva, grouping=True),
            'exempt_sum': locale.format_string('%10.2f', exempt_sum, grouping=True),
            'amount_total': locale.format_string('%10.2f', amount_total, grouping=True),
            'lines': lines,
            'address': address,

        }
        return docargs