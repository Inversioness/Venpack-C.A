# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
import base64
import logging
import locale

_logger = logging.getLogger(__name__)


class ReportMunicipalWithholding(models.TransientModel):
    _name = 'municipal.withholding'
    _description = 'Retenciones Municipales'

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
    # file = fields.Binary("Download File")
    # file_name = fields.Char(string="File Name")

    def print_report(self):
        data = {
            'model': 'municipal.withholding',
            'form': self.read()[0]
        }
        return self.env.ref('venpack_invoice.municipal_withholding_report').report_action(self, data=data)

    def cancel(self):
        return False
