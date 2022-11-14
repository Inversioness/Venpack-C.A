from odoo import api, models
import locale
import json


class MunicipalWithholdingListXlsx(models.AbstractModel):
    _name = 'report.venpack_invoice.municipal_withholding_list_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'municipal withholding list xlsx'

    def generate_xlsx_report(self, workbook, data, obj):
        report_obj = self.env['report.venpack_invoice.municipal_withholding_list']
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
        sheet.set_column('J:J', 15)


        for o in result['docs']:
            sheet.merge_range('D1:H1', "Retenciones de Impuestos Municipales Sobre Actividades Economicas Municipio Plaza", format4)
            sheet.merge_range('D2:H2', 'Fecha de Retención Desde: ' + str(result['start_date']) + ' Hasta: ' + str(result['final_date']), format6)
            sheet.merge_range('A3:C3', o.company_id.name, format1)
            sheet.merge_range('A4:C4', 'R.I.F. ' + str(o.company_id.vat), format1)
            # sheet.write('H3', "Fecha:", format1)
            # sheet.write('I3', result['fecha'], format6)
            # sheet.write('H4', "Usuario:", format1)
            # sheet.write('I4', result['username'], format6)

            sheet.write('A8', "Proveedor", format1)
            sheet.write('B8', "Nombre Proveedor", format1)
            sheet.write('C8', "Cod. Ret", format1)
            sheet.write('D8', "Ret. #", format1)
            sheet.write('E8', "Fac. Afectada", format1)
            sheet.write('F8', "# de Control", format1)
            sheet.write('G8', "Fecha", format1)
            sheet.write('H8', "%", format1)
            sheet.write('I8', "Base Imponible", format1)
            sheet.write('J8', "Monto Ret", format1)

            row = 8
            col = 0
            for dsb in result['data_municipal_listing']:
                sheet.write(row, col, dsb['provider'], format6)
                sheet.write(row, col + 1, dsb['provider_name'], format6)
                sheet.write(row, col + 2, dsb['retention_code'] if dsb['retention_code'] else " ", format6)
                sheet.write(row, col + 3, dsb['retention_number'] if dsb['retention_number'] else " ", format6)
                sheet.write(row, col + 4, dsb['affected_invoice'] if dsb['affected_invoice'] else " ", format6)
                sheet.write(row, col + 5, dsb['control_number'], format2)
                sheet.write(row, col + 6, dsb['date'], format2)
                sheet.write(row, col + 7, dsb['retention_percentage'], format6)
                sheet.write(row, col + 8, dsb['tax_base'], format2)
                sheet.write(row, col + 9, dsb['tax_withheld'], format2)
                row += 1

            sheet.merge_range(row, 6, row, 7, "Totales Generales:", format5)
            sheet.write(row, col + 8, result['tax_base_total'], format2)
            sheet.write(row, col + 9, result['tax_withheld_total'], format2)



