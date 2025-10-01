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

        # Cálculo de variables en ambas monedas: _ves (bolívares) y _rate (USD)
        tasa = docs.x_tasa if docs.x_tasa else 0
        # Inicialización
        amount_untaxed_ves = 0.0
        discount_sum_ves = 0.0
        tax_iva_ves = 0.0
        tax_base_ves = 0.0
        exempt_sum_ves = 0.0
        amount_total_ves = 0.0
        amount_untaxed_rate = 0.0
        discount_sum_rate = 0.0
        tax_iva_rate = 0.0
        tax_base_rate = 0.0
        exempt_sum_rate = 0.0
        amount_total_rate = 0.0

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
                'quantity': ili.quantity,
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

                # amount_untaxed += ili.unit_price_without_tax
                if ti.x_tipoimpuesto == 'IVA':
                    tax_base += ili.price_subtotal
                    line_iva_id = docs.line_ids.search([('name', '=', ti.name), ('move_id', '=', docs.id)])
                    tax_iva = abs(line_iva_id.amount_currency)
                    # if docs.x_tipodoc == 'Nota de Crédito':
                    #     tax_iva = line_iva_id.debit
                    # else:
                    #     tax_iva = abs(line_iva_id.amount_currency)
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


        # Cálculo de variables en ambas monedas: _ves (bolívares) y _rate (USD)
        tasa = docs.x_tasa if docs.x_tasa else 0
        # Inicialización
        amount_untaxed_ves = 0.0
        discount_sum_ves = 0.0
        tax_iva_ves = 0.0
        tax_base_ves = 0.0
        exempt_sum_ves = 0.0
        amount_total_ves = 0.0
        amount_untaxed_rate = 0.0
        discount_sum_rate = 0.0
        tax_iva_rate = 0.0
        tax_base_rate = 0.0
        exempt_sum_rate = 0.0
        amount_total_rate = 0.0

        amount_untaxed = docs.amount_untaxed

        if docs.currency_id.name == 'VES':
            # Las variables _ves son las calculadas, las _rate se obtienen dividiendo entre la tasa
            amount_untaxed_ves = amount_untaxed
            discount_sum_ves = discount_sum
            tax_iva_ves = tax_iva
            tax_base_ves = tax_base
            exempt_sum_ves = exempt_sum
            amount_total_ves = amount_total

            amount_untaxed_rate = amount_untaxed / tasa if tasa else 0
            discount_sum_rate = discount_sum / tasa if tasa else 0
            tax_iva_rate = tax_iva / tasa if tasa else 0
            tax_base_rate = tax_base / tasa if tasa else 0
            exempt_sum_rate = exempt_sum / tasa if tasa else 0
            amount_total_rate = amount_total / tasa if tasa else 0
        else:
            # amount_total = tax_iva + tax_base + exempt_sum
            # Las variables _rate son las calculadas, las _ves se obtienen multiplicando por la tasa
            amount_untaxed_rate = amount_untaxed
            discount_sum_rate = discount_sum
            tax_base_rate = tax_base
            exempt_sum_rate = exempt_sum
            tax_iva_rate = tax_iva
            amount_total_rate = amount_total

            amount_untaxed_ves = amount_untaxed * tasa if tasa else 0
            discount_sum_ves = discount_sum * tasa if tasa else 0
            tax_base_ves = amount_untaxed_ves
            exempt_sum_ves = exempt_sum * tasa if tasa else 0
            # IVA en VES: 16% del monto base en VES
            tax_iva_ves = tax_base_ves * 0.16
            amount_total_ves = amount_untaxed_ves + tax_iva_ves + exempt_sum_ves

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'amount_untaxed': amount_untaxed,
            'discount_sum': discount_sum,
            'tax_iva': tax_iva,
            'exempt_sum': exempt_sum,
            'amount_total': amount_total,
            'lines': lines,
            'address': address,
            # Variables para la otra moneda
            'amount_untaxed_ves': amount_untaxed_ves,
            'discount_sum_ves': discount_sum_ves,
            'tax_iva_ves': tax_iva_ves,
            'tax_base_ves': tax_base_ves,
            'exempt_sum_ves': exempt_sum_ves,
            'amount_total_ves': amount_total_ves,
            'amount_untaxed_rate': amount_untaxed_rate,
            'discount_sum_rate': discount_sum_rate,
            'tax_iva_rate': tax_iva_rate,
            'tax_base_rate': tax_base_rate,
            'exempt_sum_rate': exempt_sum_rate,
            'amount_total_rate': amount_total_rate,
        }
        return docargs