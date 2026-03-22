from odoo import models, fields, api

class BlankTaxReportWizard(models.TransientModel):
    _name = 'blank.tax.report.wizard'
    _description = 'Wizard para generar reportes de impuestos'

    report_type = fields.Selection([
        ('iva_listing', 'Listado IVA'),
        ('islr_listing', 'Listado ISLR'),
        ('iva_txt', 'Reporte txt IVA')
    ], string='Tipo de Reporte', required=True)
    start_date = fields.Date(string='Fecha de Inicio', required=True)
    end_date = fields.Date(string='Fecha de Fin', required=True)

    def generate_report(self):
        self.ensure_one()
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        if self.report_type == 'iva_listing':
            return self.env.ref('tax_report.iva_listing_report').report_action(self, data=data)
        elif self.report_type == 'islr_listing':
            return self.env.ref('tax_report.islr_listing_report').report_action(self, data=data)
        elif self.report_type == 'iva_txt':
            return self.env.ref('tax_report.iva_txt_report').report_action(self, data=data)
