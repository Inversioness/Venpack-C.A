from odoo import api, models
from datetime import datetime


class IvaListingCustomization(models.AbstractModel):
    _inherit = 'report.tax_report.iva_listing'
    _description = 'Customization of listado de iva: return empty docargs when no docids'

    @api.model
    def _get_report_values(self, docids, data=None):
        # If no docids are provided, return a minimal/empty docargs as requested
        if not docids:
            docs = self.env['account.move'].search([
                ('company_id', '=', self.env.company.id)
            ], limit=1)

            # Expect data to contain start_date and end_date in ISO format (YYYY-MM-DD)
            start_date = ''
            final_date = ''
            if data:
                try:
                    start_date = datetime.strptime(data.get('start_date', ''), '%Y-%m-%d').strftime('%d/%m/%Y')
                except Exception:
                    start_date = data.get('start_date', '')
                try:
                    final_date = datetime.strptime(data.get('end_date', ''), '%Y-%m-%d').strftime('%d/%m/%Y')
                except Exception:
                    final_date = data.get('end_date', '')

            docargs = {
                'doc_ids': docids,
                'doc_model': 'account.move',
                'data': data,
                'docs': docs,
                'fecha': datetime.today().strftime('%d/%m/%Y'),
                'username': self.env.user.name,
                'start_date': start_date,
                'final_date': final_date,
                # Return numeric zeros so float widget can round/format them
                'tax_base_total': 0.0,
                'tax_iva_total': 0.0,
                'iva_withheld_total': 0.0,
                'data_iva_listing': [],
            }
            return docargs

        # If docids exist, delegate to the original implementation in tax_report
        return super(IvaListingCustomization, self)._get_report_values(docids, data=data)
