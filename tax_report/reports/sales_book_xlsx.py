from odoo import api, models
import locale
import json


class SalesBookXlsx(models.AbstractModel):
    _name = 'report.tax_report.sales_book_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Libro de Ventas xlsx'

    def generate_xlsx_report(self, workbook, data, obj):
        report_obj = self.env['report.tax_report.sales_book']
        result = report_obj._get_report_values(obj.ids, data)

        sheet = workbook.add_worksheet('Libro de Ventas')
        format1 = workbook.add_format({'align': 'Justify', 'bold': True})
        format2 = workbook.add_format({'align': 'right', 'bold': False})
        format3 = workbook.add_format({'align': 'left', 'bold': False})
        format4 = workbook.add_format({'align': 'center', 'bold': True})
        format5 = workbook.add_format({'align': 'right', 'bold': True})
        format6 = workbook.add_format({'align': 'center', 'bold': False})
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 35)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 15)
        sheet.set_column('O:O', 15)
        sheet.set_column('P:P', 15)
        sheet.set_column('Q:Q', 15)
        for o in result['docs']:
            sheet.merge_range('E1:H1', "Libro de Ventas", format4)
            sheet.merge_range('A3:D3', o.company_id.name, format1)
            sheet.merge_range('G3:J3', 'DESDE: ' + str(o.start_date) + ' HASTA: ' + str(o.final_date), format1)
            sheet.merge_range('A4:D4', 'R.I.F. ' + str(o.company_id.vat), format1)
            sheet.merge_range('A5:D5', 'N.I.T.', format1)
            sheet.merge_range('M7:O7', "VENTAS INTERNAS O EXPORTACION GRAVADAS", format1)
            sheet.write('A8', "No.", format1)
            sheet.write('B8', "Fecha Factura", format1)
            sheet.write('C8', "R.I.F.", format1)
            sheet.write('D8', "Nombre del Cliente o Razón Social", format1)
            sheet.write('E8', "Nº de Factura", format1)
            sheet.write('F8', "Nº Control de Factura", format1)
            sheet.write('G8', "Nº Nota Débito", format1)
            sheet.write('H8', "Nº Nota Crédito", format1)
            sheet.write('I8', "Tipo de Trans.", format1)
            sheet.write('J8', "Nº de Factura Afectada", format1)
            sheet.write('K8', "Total Ventas (Incluye IVA)", format1)
            sheet.write('L8', "Ventas Internas No Gravadas", format1)
            sheet.write('M8', "Base Imponible", format1)
            sheet.write('N8', "% Alicuota", format1)
            sheet.write('O8', "Impuesto IVA", format1)
            sheet.write('P8', "% de Retención", format1)
            sheet.write('Q8', "Iva Retenido (por el comprador)", format1)
            sheet.write('R8', "Nº Comp IVA.", format1)

            row = 8
            col = 0
            for dsb in result['data_sales_book']:
                sheet.write(row, col, dsb['number'], format2)
                sheet.write(row, col + 1, dsb['date'], format3)
                sheet.write(row, col + 2, dsb['rif_supplier'], format3)
                sheet.write(row, col + 3, dsb['customer_name'], format3)
                sheet.write(row, col + 4, dsb['invoice_number'], format3)
                sheet.write(row, col + 5, dsb['control_number'], format3)
                sheet.write(row, col + 6, dsb['debit_note'], format3)
                sheet.write(row, col + 7, dsb['credit_note'], format3)
                sheet.write(row, col + 8, dsb['transaction_type'], format2)
                sheet.write(row, col + 9, dsb['affected_invoice_number'], format2)
                sheet.write(row, col + 10, dsb['amount_total'], format2)
                sheet.write(row, col + 11, dsb['exempt_amount'], format2)
                sheet.write(row, col + 12, dsb['tax_base'], format2)
                sheet.write(row, col + 13, dsb['iva_percentage'], format2)
                sheet.write(row, col + 14, dsb['tax_iva'], format2)
                sheet.write(row, col + 15, dsb['retention_percentage'], format2)
                sheet.write(row, col + 16, dsb['iva_withheld'], format2)
                sheet.write(row, col + 17, dsb['iva_receipt_number'], format2)
                row += 1

            print(row)
            sheet.merge_range(row, 8, row, 9, "Totales Generales:", format5)
            sheet.write(row, col + 10, result['sum_amount_total'], format2)
            sheet.write(row, col + 11, result['sum_exempt_amount'], format2)
            sheet.write(row, col + 12, result['sum_tax_base_amount'], format2)
            sheet.write(row, col + 14, result['sum_tax_iva_amount'], format2)
            sheet.write(row, col + 16, result['sum_iva_withheld'], format2)

            row = row + 3
            # Cuadro Resumen
            sheet.write(row, col + 6, 'Base Imponible', format1)
            sheet.write(row, col + 8, 'Débito Fiscal', format1)
            sheet.write(row, col + 10, 'IVA Retenido por el Comprador', format1)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "Total: Ventas Internas No Gravadas", format3)
            sheet.write(row, col + 5, '40', format6)
            sheet.write(row, col + 6, result['sum_exempt_amount'], format6)
            sheet.write(row, col + 7, '', format6)
            sheet.write(row, col + 8, '', format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, '', format6)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "Total de las: Ventas de Exportación", format3)
            sheet.write(row, col + 5, '41', format6)
            sheet.write(row, col + 6, '0,00', format6)
            sheet.write(row, col + 7, '', format6)
            sheet.write(row, col + 8, '0,00', format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, '0,00', format6)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "", format3)
            sheet.write(row, col + 5, '', format6)
            sheet.write(row, col + 6, '', format6)
            sheet.write(row, col + 7, '', format6)
            sheet.write(row, col + 8, '', format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, '', format6)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "Total de las: Ventas Internas Afectas solol Alicuota Genera", format3)
            sheet.write(row, col + 5, '42', format6)
            sheet.write(row, col + 6, result['sum_tax_base_amount'], format6)
            sheet.write(row, col + 7, '43', format6)
            sheet.write(row, col + 8, result['sum_tax_iva_amount'], format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, result['sum_iva_withheld'], format6)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "Total de las: Ventas Internas Afectas solo Alicuota General + Adicional ", format3)
            sheet.write(row, col + 5, '442', format6)
            sheet.write(row, col + 6, '0,00', format6)
            sheet.write(row, col + 7, '563', format6)
            sheet.write(row, col + 8, '0,00', format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, '0,00', format6)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "Total de las: Ventas Internas Afectas en Alicuota Reducida", format3)
            sheet.write(row, col + 5, '443', format6)
            sheet.write(row, col + 6, '0,00', format6)
            sheet.write(row, col + 7, '453', format6)
            sheet.write(row, col + 8, '0,00', format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, '0,00', format6)

            row = row + 1
            sheet.write(row, col + 5, '46', format6)
            sheet.write(row, col + 6, result['total_tax_base_column'], format6)
            sheet.write(row, col + 7, '47', format6)
            sheet.write(row, col + 8, result['sum_tax_iva_amount'], format6)
            sheet.write(row, col + 9, '54', format6)
            sheet.write(row, col + 10, result['sum_iva_withheld'], format6)



