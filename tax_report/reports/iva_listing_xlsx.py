from odoo import api, models
import locale
import json


class IvaListingXlsx(models.AbstractModel):
    _name = 'report.tax_report.iva_listing_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Listado IVA xlsx'

    def generate_xlsx_report(self, workbook, data, obj):
        report_obj = self.env['report.tax_report.iva_listing']
        result = report_obj._get_report_values(obj.ids, data)

        sheet = workbook.add_worksheet('Listado IVA')
        format1 = workbook.add_format({'align': 'Justify', 'bold': True})
        format2 = workbook.add_format({'align': 'right', 'bold': False})
        format3 = workbook.add_format({'align': 'left', 'bold': False})
        format4 = workbook.add_format({'align': 'center', 'bold': True})
        format5 = workbook.add_format({'align': 'right', 'bold': True})
        format6 = workbook.add_format({'align': 'center', 'bold': False})
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 35)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 10)
        sheet.set_column('I:I', 15)


        for o in result['docs']:
            sheet.merge_range('D1:G1', "Retenciones de IVA General", format4)
            sheet.merge_range('D2:G2', 'Fecha de Retención Desde: ' + str(result['start_date']) + ' Hasta: ' + str(result['final_date']), format6)
            sheet.merge_range('A3:C3', o.company_id.name, format1)
            sheet.merge_range('A4:C4', 'R.I.F. ' + str(o.company_id.vat), format1)
            sheet.write('H3', "Fecha:", format1)
            sheet.write('I3', result['fecha'], format6)
            sheet.write('H4', "Usuario:", format1)
            sheet.write('I4', result['username'], format6)

            sheet.write('A8', "Tipo Doc", format1)
            sheet.write('B8', "Numero Doc", format1)
            sheet.write('C8', "Fecha", format1)
            sheet.write('D8', "Nro Transaccion", format1)
            sheet.write('E8', "Proveedor", format1)
            sheet.write('F8', "Monto Base", format1)
            sheet.write('G8', "Monto Iva", format1)
            sheet.write('H8', "% Ret", format1)
            sheet.write('I8', "Monto Retenido", format1)

            row = 8
            col = 0
            for dsb in result['data_iva_listing']:
                sheet.write(row, col, dsb['document_type'], format6)
                sheet.write(row, col + 1, dsb['document_number'] if dsb['document_number'] else " ", format6)
                sheet.write(row, col + 2, dsb['date'], format6)
                sheet.write(row, col + 3, dsb['transaction_number'] if dsb['transaction_number'] else " ", format6)
                sheet.write(row, col + 4, dsb['provider_name'], format6)
                sheet.write(row, col + 5, dsb['tax_base'], format2)
                sheet.write(row, col + 6, dsb['tax_iva'], format2)
                sheet.write(row, col + 7, dsb['retention_percentage'], format6)
                sheet.write(row, col + 8, dsb['th_iva_withheld'], format2)
                row += 1

            sheet.merge_range(row, 3, row, 4, "Totales Generales:", format5)
            sheet.write(row, col + 5, result['tax_base_total'], format2)
            sheet.write(row, col + 6, result['tax_iva_total'], format2)
            sheet.write(row, col + 8, result['iva_withheld_total'], format2)



