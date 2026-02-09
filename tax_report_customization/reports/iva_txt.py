from odoo import api, models
from datetime import datetime


class IvaTxtCustomization(models.AbstractModel):
    _inherit = 'report.tax_report.iva_txt'
    _description = 'Customization of iva txt: return placeholder when no docids'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not docids:
            data_txt_iva = []
            iva_txt_line = {
                'rif_company': self.env.company.vat,
                'fiscal_period': '',
                'date': 0,
                'column_4': 0,
                'transaction_type': 0,
                'rif_supplier': 0,
                'invoice_number': 0,
                'control_number': 0,
                'amount_total': 0,
                'tax_base': 0,
                'iva_withheld': 0,
                'affected_invoice_number': 0,
                'voucher_number': 0,
                'exempt_amount': 0,
                'retention_percentage': 0,
                'column_16': 0,
            }
            # try to build fiscal_period from data.start_date if provided
            if data and data.get('start_date'):
                try:
                    iva_txt_line['fiscal_period'] = data['start_date'].replace('-', '')[:6]
                except Exception:
                    iva_txt_line['fiscal_period'] = data.get('start_date', '')

            data_txt_iva.append(iva_txt_line)
            docargs = {
                'doc_ids': docids,
                'doc_model': 'account.move',
                'data': data,
                'docs': [],
                'data_txt_iva': data_txt_iva,
            }
            return docargs

        return super(IvaTxtCustomization, self)._get_report_values(docids, data=data)
