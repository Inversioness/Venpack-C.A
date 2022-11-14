from odoo import api, models
import locale
from odoo.exceptions import ValidationError


class PalmaSuitesInvoice(models.AbstractModel):
    _name = 'report.venpack_invoice.tracking_guide'
    _description = 'Guia de Despacho PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('funcion para obtener datos del cliente para el reporte')
        locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
        docs = self.env['stock.picking'].browse(docids[0])
        #sale_order_id = self.env['sale.order'].search([('name', '=', docs.origin)])
        # print(docs.sale_id)
        # if not docs.sale_id.invoice_ids:
        #     raise ValidationError("No existe una factura asignada a este pedido")

        # for mli in docs.move_line_ids:


        amount_untaxed = 0.0
        exempt_sum = 0.0
        tax_base = 0.0
        percentage = ''
        tax_iva = 0.0
        iva_withheld = 0.0
        amount_total = 0.0
        discount_sum = 0.0

        # for ili in docs.invoice_line_ids:
        #     for ti in ili.tax_ids:
        #         if ili.discount:
        #             discount_sum += round(ili.price_unit * (ili.discount / 100), 2)
        #         else:
        #             discount_sum += 0.0
        #
        #         amount_untaxed += ili.unit_price_without_tax
        #         if ti.x_tipoimpuesto == 'IVA':
        #             tax_base += ili.price_subtotal
        #             line_iva_id = docs.line_ids.search([('name', '=', ti.name), ('move_id', '=', docs.id)])
        #             if docs.x_tipodoc == 'Nota de Crédito':
        #                 tax_iva = line_iva_id.debit
        #             else:
        #                 tax_iva = line_iva_id.credit
        #             percentage = line_iva_id.name
        #         if ti.x_tipoimpuesto == 'EXENTO':
        #             exempt_sum += ili.price_subtotal
        #         if ti.x_tipoimpuesto == 'RIVA':
        #             line_riva_id = docs.line_ids.search([('name', '=', ti.name), ('move_id', '=', docs.id)])
        #             if docs.x_tipodoc == 'Nota de Crédito':
        #                 iva_withheld = line_riva_id.debit
        #             else:
        #                 iva_withheld = line_riva_id.credit
        #
        # amount_total = tax_iva + tax_base + exempt_sum
        #
        # if percentage != '':
        #     retention_percentage = percentage[4:]
        # else:
        #     retention_percentage = ''

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            # 'amount_untaxed': locale.format_string('%10.2f', docs.amount_untaxed, grouping=True),
            'discount_sum': locale.format_string('%10.2f', discount_sum, grouping=True),
            'tax_iva': locale.format_string('%10.2f', tax_iva, grouping=True),
            'exempt_sum': locale.format_string('%10.2f', exempt_sum, grouping=True),
            'amount_total': locale.format_string('%10.2f', amount_total, grouping=True),
        }
        return docargs
