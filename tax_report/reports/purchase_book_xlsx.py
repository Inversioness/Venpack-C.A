from odoo import api, models
import locale
import json


class PurchaseBookXlsx(models.AbstractModel):
    _name = 'report.tax_report.purchase_book_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Libro de Compras xlsx'

    def generate_xlsx_report(self, workbook, data, obj):
        report_obj = self.env['report.tax_report.purchase_book']
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
            sheet.merge_range('E1:H1', "Libro de COmpras", format4)
            sheet.merge_range('A3:D3', o.company_id.name, format1)
            sheet.merge_range('G3:J3', 'DESDE: ' + str(o.start_date) + ' HASTA: ' + str(o.final_date), format1)
            sheet.merge_range('A4:D4', 'R.I.F. ' + str(o.company_id.vat), format1)
            sheet.merge_range('A5:D5', 'N.I.T.', format1)
            sheet.merge_range('M7:O7', "VENTAS INTERNAS O EXPORTACION GRAVADAS", format1)
            sheet.write('A8', "No.", format1)
            sheet.write('B8', "Fecha Factura", format1)
            sheet.write('C8', "R.I.F.", format1)
            sheet.write('D8', "Nombre del Proveedor o Razón Social", format1)
            sheet.write('E8', "Tipo Prov.", format1)
            sheet.write('F8', "Nº Comprob", format1)
            sheet.write('G8', "Nº Planilla Imp C80 o C81", format1)
            sheet.write('H8', "Nº Expediente Importación", format1)
            sheet.write('I8', "Nº de Factura", format1)
            sheet.write('J8', "Nº Control de Factura", format1)
            sheet.write('K8', "Nº Nota Débito", format1)
            sheet.write('L8', "Nº Nota Crédito", format1)
            sheet.write('M8', "Tipo de Trans.", format1)
            sheet.write('N8', "Nº de Factura Afectada", format1)
            sheet.write('O8', "Total Compras (Incluye IVA)", format1)
            sheet.write('P8', "Compras sin Derecho a IVA", format1)
            sheet.write('Q8', "Base Imponible", format1)
            sheet.write('R8', "% Alicuota", format1)
            sheet.write('S8', "Impuesto IVA", format1)
            sheet.write('T8', "% de Retención", format1)
            sheet.write('U8', "Iva Retenido al Vendedor", format1)


            row = 8
            col = 0
            for dsb in result['data_purchase_book']:
                sheet.write(row, col, dsb['number'], format2)
                sheet.write(row, col + 1, dsb['date'], format3)
                sheet.write(row, col + 2, dsb['rif_supplier'], format3)
                sheet.write(row, col + 3, dsb['provider_name'], format3)
                sheet.write(row, col + 4, dsb['provider_type'], format3)
                sheet.write(row, col + 5, dsb['voucher_number'] if dsb['voucher_number'] else '', format3)
                sheet.write(row, col + 6, dsb['import_template_number'] if dsb['import_template_number'] else '', format3)
                sheet.write(row, col + 7, dsb['no_proceedings_import'] if dsb['no_proceedings_import'] else '', format3)
                sheet.write(row, col + 8, dsb['invoice_number'], format3)
                sheet.write(row, col + 9, dsb['control_number'] if dsb['control_number'] else '', format3)
                sheet.write(row, col + 10, dsb['debit_note'], format3)
                sheet.write(row, col + 11, dsb['credit_note'], format3)
                sheet.write(row, col + 12, dsb['transaction_type'], format2)
                sheet.write(row, col + 13, dsb['affected_invoice_number'], format2)
                sheet.write(row, col + 14, dsb['amount_total'], format2)
                sheet.write(row, col + 15, dsb['exempt_amount'], format2)
                sheet.write(row, col + 16, dsb['tax_base'], format2)
                sheet.write(row, col + 17, dsb['iva_percentage'], format2)
                sheet.write(row, col + 18, dsb['tax_iva'], format2)
                sheet.write(row, col + 19, dsb['retention_percentage'], format2)
                sheet.write(row, col + 20, dsb['iva_withheld'], format2)
                row += 1

            sheet.merge_range(row, 12, row, 13, "Totales Generales:", format5)
            sheet.write(row, col + 14, result['sum_amount_total'], format2)
            sheet.write(row, col + 15, result['sum_exempt_amount'], format2)
            sheet.write(row, col + 16, result['sum_tax_base_amount'], format2)
            sheet.write(row, col + 18, result['sum_tax_iva_amount'], format2)
            sheet.write(row, col + 20, result['sum_iva_withheld'], format2)

            row = row + 3
            # Cuadro Resumen
            sheet.write(row, col + 6, 'Base Imponible', format1)
            sheet.write(row, col + 8, 'Crédito Fiscal', format1)
            sheet.write(row, col + 10, 'IVA Retenido a Terceros', format1)
            sheet.write(row, col + 12, 'Anticipo IVA', format1)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "Total: Compras Exentas y/o Sin Derecho a Crédito Fiscal ", format3)
            sheet.write(row, col + 5, '30', format6)
            sheet.write(row, col + 6, result['sum_exempt_amount'], format6)
            sheet.write(row, col + 7, '', format6)
            sheet.write(row, col + 8, '', format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, '', format6)
            sheet.write(row, col + 11, '', format6)
            sheet.write(row, col + 12, '', format6)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "Total de las: Compras Importación Afectas solo Alicuota General", format3)
            sheet.write(row, col + 5, '31', format6)
            sheet.write(row, col + 6, '0,00', format6)
            sheet.write(row, col + 7, '32', format6)
            sheet.write(row, col + 8, '0,00', format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, '', format6)
            sheet.write(row, col + 11, '', format6)
            sheet.write(row, col + 12, '', format6)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "Total de las: Compras Importación Afectas solo Alicuota General + Adicional", format3)
            sheet.write(row, col + 5, '312', format6)
            sheet.write(row, col + 6, '0,00', format6)
            sheet.write(row, col + 7, '322', format6)
            sheet.write(row, col + 8, '0,00', format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, '', format6)
            sheet.write(row, col + 11, '', format6)
            sheet.write(row, col + 12, '', format6)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "Total de las: Compras Importación Afectas en Alicuota Reducida", format3)
            sheet.write(row, col + 5, '313', format6)
            sheet.write(row, col + 6, '0,00', format6)
            sheet.write(row, col + 7, '323', format6)
            sheet.write(row, col + 8, '0,00', format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, '', format6)
            sheet.write(row, col + 11, '', format6)
            sheet.write(row, col + 12, '', format6)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "Total de las: Compras Internas Afectas solo Alicuota General", format3)
            sheet.write(row, col + 5, '33', format6)
            sheet.write(row, col + 6, result['sum_tax_base_amount'], format6)
            sheet.write(row, col + 7, '34', format6)
            sheet.write(row, col + 8, result['sum_tax_iva_amount'], format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, result['sum_iva_withheld'], format6)
            sheet.write(row, col + 11, '', format6)
            sheet.write(row, col + 12, '', format6)

            row = row + 1
            sheet.merge_range(row, 1, row, 4, "Total de las: Compras Internas Afectas solo Alicuota General + Adicional", format3)
            sheet.write(row, col + 5, '332', format6)
            sheet.write(row, col + 6, '0,00', format6)
            sheet.write(row, col + 7, '342', format6)
            sheet.write(row, col + 8, '0,00', format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, '', format6)
            sheet.write(row, col + 11, '', format6)
            sheet.write(row, col + 12, '', format6)

            row = row + 1
            sheet.merge_range(row, 1, row, 4,
                              "Total de las: Compras Internas Afectas en Alicuota Reducida", format3)
            sheet.write(row, col + 5, '333', format6)
            sheet.write(row, col + 6, '0,00', format6)
            sheet.write(row, col + 7, '343', format6)
            sheet.write(row, col + 8, '0,00', format6)
            sheet.write(row, col + 9, '', format6)
            sheet.write(row, col + 10, '', format6)
            sheet.write(row, col + 11, '', format6)
            sheet.write(row, col + 12, '', format6)

            row = row + 1
            sheet.write(row, col + 5, '35', format6)
            sheet.write(row, col + 6, result['total_tax_base_column'], format6)
            sheet.write(row, col + 7, '36', format6)
            sheet.write(row, col + 8, result['sum_tax_iva_amount'], format6)
            sheet.write(row, col + 9, '65', format6)
            sheet.write(row, col + 10, result['sum_iva_withheld'], format6)
            sheet.write(row, col + 11, '', format6)
            sheet.write(row, col + 12, '0,00', format6)



