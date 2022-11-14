from odoo import api, models
import locale
import json


class PurchaseBookXlsx(models.AbstractModel):
    _name = 'report.tax_report.islr_listing_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Listado ISLR xlsx'

    def generate_xlsx_report(self, workbook, data, obj):
        report_obj = self.env['report.tax_report.islr_listing']
        result = report_obj._get_report_values(obj.ids, data)

        sheet = workbook.add_worksheet('Libro de Ventas')
        format1 = workbook.add_format({'align': 'Justify', 'bold': True})
        format2 = workbook.add_format({'align': 'right', 'bold': False})
        format3 = workbook.add_format({'align': 'left', 'bold': False})
        format4 = workbook.add_format({'align': 'center', 'bold': True})
        format5 = workbook.add_format({'align': 'right', 'bold': True})
        format6 = workbook.add_format({'align': 'center', 'bold': False})
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 5)
        sheet.set_column('D:D', 10)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 10)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)

        for o in result['docs']:
            sheet.merge_range('E1:H1', "Retenciones de Impusto Sobre la Renta en Proveedores", format4)
            sheet.merge_range('A3:C3', o.company_id.name, format1)
            sheet.merge_range('E2:H2', 'Fecha de Retención Desde: ' + str(result['start_date']) + ' Hasta: ' + str(result['final_date']), format6)
            sheet.merge_range('A4:C4', 'R.I.F. ' + str(o.company_id.vat), format1)
            sheet.write('J3', "Fecha:", format1)
            sheet.write('K3', result['fecha'], format6)
            sheet.write('J4', "Usuario:", format1)
            sheet.write('K4', result['username'], format6)

            sheet.write('A8', "Proveedor", format1)
            sheet.write('B8', "Nombre Proveedor", format1)
            sheet.write('C8', "Cod Ret", format1)
            sheet.write('D8', "Retenc.#", format1)
            sheet.write('E8', "Tipo Doc", format1)
            sheet.write('F8', "Documento", format1)
            sheet.write('G8', "Nro Control", format1)
            sheet.write('H8', "Fecha Ret", format1)
            sheet.write('I8', "%", format1)
            sheet.write('J8', "Base Imponible", format1)
            sheet.write('K8', "Monto Retención", format1)

            row = 8
            col = 0
            for dsb in result['data_islr_listing']:
                sheet.write(row, col, dsb['provider'], format2)
                sheet.write(row, col + 1, dsb['provider_name'], format3)
                sheet.write(row, col + 2, dsb['retention_code'], format3)
                sheet.write(row, col + 3, dsb['retention_number'], format3)
                sheet.write(row, col + 4, dsb['document_type'], format3)
                sheet.write(row, col + 5, dsb['document'] if dsb['document'] else " ", format3)
                sheet.write(row, col + 6, dsb['control_number'] if dsb['control_number'] else " ", format3)
                sheet.write(row, col + 7, dsb['retention_date'], format3)
                sheet.write(row, col + 8, dsb['retention_percentage'], format3)
                sheet.write(row, col + 9, dsb['tax_base'], format3)
                sheet.write(row, col + 10, dsb['tax_withheld'], format3)
                row += 1

            sheet.merge_range(row, 7, row, 8, "Totales Generales:", format5)
            sheet.write(row, col + 9, result['tax_base_total'], format2)
            sheet.write(row, col + 10, result['tax_withheld_total'], format2)



