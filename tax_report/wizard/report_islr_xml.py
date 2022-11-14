# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
import base64
import logging
import locale

_logger = logging.getLogger(__name__)


class ReportIslrXml(models.TransientModel):
    _name = 'islr.xml'
    _description = 'Report Islr Xml'

    def get_years():
        year_list = []
        for i in range(2016, 2036):
            year_list.append((str(i), str(i)))
        return year_list

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)
    month = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
                              ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
                              ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')],
                             string='Mes', required=True)
    year = fields.Selection(get_years(), string='Año', required=True)
    # from_date = fields.Date(string='Desde', required=True)
    # to_date = fields.Date(string='Hasta', required=True)
    file = fields.Binary("Download File")
    file_name = fields.Char(string="File Name")

    @staticmethod
    def date_range(month, year):
        start_date = datetime.strptime('1-' + month + '-' + year, '%d-%m-%Y')
        end_date = ''

        if int(month) == 12:
            end_date_aux = datetime.strptime('1-' + '1' + '-' + str(int(year) + 1), '%d-%m-%Y')
            end_date = end_date_aux - timedelta(seconds=1)
        else:
            end_date_aux = datetime.strptime('1-' + str(int(month) + 1) + '-' + year,
                                                      '%d-%m-%Y')
            end_date = end_date_aux - timedelta(seconds=1)

        return start_date, end_date

    @staticmethod
    def string_format(rif):
        characters = "-./_ "
        for x in range(len(characters)):
            rif = rif.replace(characters[x], "")
        return rif

    @staticmethod
    def retention_code_format(ret_code):
        if len(ret_code) >= 3:
            retention_number = ret_code
        elif len(ret_code) == 2:
            retention_number = '0' + str(ret_code)
        elif len(ret_code) == 1:
            retention_number = '00' + str(ret_code)
        else:
            retention_number = ''
        return retention_number

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
                    pass
                    # print('No existe tax para la linea de venta')
        else:
            pass
            # print('No existe lineas de venta')

        return data_transform

    def build_taxes(self):
        from_date, to_date = self.date_range(self.month, self.year)
        period = from_date.strftime('%Y%m')
        invoice_ids = self.env['account.move'].search(
            [('date', '>=', from_date), ('date', '<=', to_date), ('x_ncontrol', '!=', False), ('state', '=', 'posted')]).sorted(key=lambda r: r.date)
        data_islr_listing = []
        for invoice in invoice_ids:
            invoice_line_group_by_name_tax = self.transform_and_group_by_item(data=invoice.invoice_line_ids, item_group="tax_ids", sub_item_group='x_tipoimpuesto')
            if invoice_line_group_by_name_tax:
                for key, value in invoice_line_group_by_name_tax.items():
                    tax_withheld = 0.0
                    price_subtotal = 0
                    line_id = invoice.line_ids.search([('name', '=', key), ('move_id', '=', invoice.id)])
                    # tax_withheld_line = abs(line_id.amount_currency)
                    tax_withheld += abs(line_id.amount_currency)
                    account_tax_id = self.env['account.tax'].search([('name', '=', key)])
                    retention_code = str(account_tax_id.x_conceptoret)
                    retention_number = key[:6]
                    retention_percentage = locale.format_string('%10.2f', account_tax_id.amount, grouping=True).replace("-", "")
                    retention_percentage = round(abs(account_tax_id.amount), 2)

                    for ili in value:
                        price_subtotal += ili.price_subtotal

                    if invoice.currency_id.name != 'VES':
                        price_subtotal = price_subtotal * invoice.x_tasa
                        tax_withheld = tax_withheld * invoice.x_tasa

                    if invoice.x_tipodoc == 'Nota de Crédito':
                        price_subtotal = -1 * price_subtotal if price_subtotal != 0 else price_subtotal
                        tax_withheld = -1 * tax_withheld if tax_withheld != 0 else tax_withheld

                    # tax_base_total += price_subtotal
                    # tax_withheld_total += tax_withheld

                    # amount_price_subtotal = locale.format_string('%10.2f', price_subtotal, grouping=True)
                    amount_price_subtotal = round(price_subtotal, 2)

                    date = invoice.date.strftime('%d/%m/%Y')
                    rif_supplier = self.string_format(invoice.fiscal_provider.vat)
                    provider_name = invoice.fiscal_provider.name
                    if invoice.x_tipodoc == 'Factura':
                        document_type = 'FAC'
                    elif invoice.x_tipodoc == 'Nota de Crédito':
                        document_type = 'NC'
                    elif invoice.x_tipodoc == 'Nota de Débito':
                        document_type = 'ND'
                    else:
                        document_type = ''

                    invoice_islr_data = {
                        'provider': rif_supplier,
                        'provider_name': provider_name,
                        'retention_code': self.retention_code_format(retention_code),
                        'retention_number': retention_number,
                        'document_type': document_type,
                        'document': self.string_format(invoice.ref) if len(invoice.ref) <= 10 else self.string_format(invoice.ref)[-10:],
                        'control_number': self.string_format(invoice.x_ncontrol),
                        'retention_date': date,
                        'retention_percentage': retention_percentage,
                        'tax_base': amount_price_subtotal,
                        'tax_withheld': round(tax_withheld, 2)
                    }
                    data_islr_listing.append(invoice_islr_data)
        return data_islr_listing, period

    def generar_xml(self):
        islr_list, period = self.build_taxes()
        if islr_list:
            print("pase por aqui", islr_list)
            # xml = ET.Element('xml', encoding="ISO-8859-1")
            xml = ET.Element("RelacionRetencionesISLR", RifAgente=self.string_format(self.company_id.vat), Periodo=period)
            for islr in islr_list:
                dt = ET.SubElement(xml, "DetalleRetencion")

                rif = ET.SubElement(dt, "RifRetenido")
                rif.text = str(islr['provider'])

                nf = ET.SubElement(dt, "NumeroFactura")
                nf.text = str(islr['document'])

                nc = ET.SubElement(dt, "NumeroControl")
                nc.text = str(islr['control_number'])

                fo = ET.SubElement(dt, "FechaOperacion")
                fo.text = str(islr['retention_date'])

                cc = ET.SubElement(dt, "CodigoConcepto")
                cc.text = str(islr['retention_code'])

                mo = ET.SubElement(dt, "MontoOperacion")
                mo.text = str(islr['tax_base'])

                pr = ET.SubElement(dt, "PorcentajeRetencion")
                pr.text = str(islr['retention_percentage'])

            # Crear archivo xml
            # xmlstr = ET.tostring(xml)
            # ET.indent(xml, space=' ', level=0)
            xmlstr = ET.tostring(xml, encoding="ISO-8859-1")
            file = base64.encodebytes(xmlstr)
            self.file = file
            self.file_name = str('ISLR_XML') + '.xml'
            view = self.env.ref('tax_report.report_islr_xml_wizard_form')

            return {
                'res_id': self.id,
                'name': 'Files to Download',
                'binding_view_types': 'form',
                'view_mode': 'form',
                'res_model': 'islr.xml',
                'type': 'ir.actions.act_window',
                'view_id': view.id,
                'target': 'new',
            }

    def cancel(self):
        return False
