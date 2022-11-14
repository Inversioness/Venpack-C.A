# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _


class CustomResCompany(models.Model):
    _inherit = 'res.company'
    _description = "Modificar modulo de res company"

    x_patent_number = fields.Char(string='No Patente', default=False)
