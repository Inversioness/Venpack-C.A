from odoo import api, models
import locale
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class IslrVoucher(models.AbstractModel):
    _name = 'report.tax_report.islr_voucher'
    _description = 'comprobante de retencion de islr pdf'

    @staticmethod
    def transform_and_group_by_item(data: list, item_group: str, sub_item_group: str) -> dict:
        data_transform = {}
        if data:
            for elem in data:
                if elem[item_group]:
                    for elem2 in elem[item_group]:
                        if elem2[sub_item_group] == 'ISLR':
                            if elem2['name'] in data_transform:
                                data_transform[elem2['name']].append(elem)
                            else:
                                data_transform[elem2['name']] = [elem]
                else:
                    print('No existe tax para la linea de venta')
        else:
            print('No existe lineas de venta')

        return data_transform

    @api.model
    def _get_report_values(self, docids, data=None):
        print('funcion para obtener datos del cliente para el reporte')
        locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
        docs = self.env['account.move'].browse(docids[0])

        data_islr = []
        tax_withheld = 0.0

        invoice_line_group_by_name_tax = self.transform_and_group_by_item(data=docs.invoice_line_ids, item_group="tax_ids", sub_item_group='x_tipoimpuesto')

        for key, value in invoice_line_group_by_name_tax.items():
            line_id = docs.line_ids.search([('name', '=', key), ('move_id', '=', docs.id)])
            tax_withheld_line = abs(line_id.amount_currency)
            tax_withheld += abs(line_id.amount_currency)

            account_tax_id = self.env['account.tax'].search([('name', '=', key)])

            if docs.currency_id.name != 'VES':
                tax_withheld_line = tax_withheld_line * docs.x_tasa

            if docs.x_tipodoc == 'Nota de Crédito':
                tax_withheld_line = -1 * tax_withheld_line if tax_withheld_line != 0 else tax_withheld_line

            islr_voucher_line = {
                'payment_date': docs.invoice_date,
                'document_number': docs.ref,
                'control_No': docs.x_ncontrol,
                'amount_paid': '0,0',
                # 'amount_document': '0,0',
                # 'amount_obt': 0.0,
                'sustraendo': account_tax_id.x_rebaja,
                'retention_percentage': locale.format_string('%10.2f', account_tax_id.amount, grouping=True).replace("-", ""),
                'ret_cod': key[:6],
                'ret_con': ' [' + str(account_tax_id.x_conceptoret) + ']',
                'description': key[7:],
                'tax_withheld_line': locale.format_string('%10.2f', tax_withheld_line, grouping=True)
            }

            price_subtotal = 0.0
            for ili in value:
                price_subtotal += ili.price_subtotal

            if docs.currency_id.name != 'VES':
                price_subtotal = price_subtotal * docs.x_tasa

            if docs.x_tipodoc == 'Nota de Crédito':
                price_subtotal = -1 * price_subtotal if price_subtotal != 0 else price_subtotal

            amount_price_subtotal = locale.format_string('%10.2f', price_subtotal, grouping=True)

            islr_voucher_line['amount_obt'] = amount_price_subtotal

            data_islr.append(islr_voucher_line)

        if docs.currency_id.name != 'VES':
            tax_withheld = tax_withheld * docs.x_tasa

        if docs.x_tipodoc == 'Nota de Crédito':
            tax_withheld = -1 * tax_withheld if tax_withheld != 0 else tax_withheld

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'data_islr': data_islr,
            'tax_withheld': locale.format_string('%10.2f', tax_withheld, grouping=True),
        }
        return docargs
