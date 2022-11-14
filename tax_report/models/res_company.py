# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, exceptions, _


class CustomResCompany(models.Model):
    _inherit = 'res.company'
    _description = "Modificar modulo de res company"

    sello = fields.Binary(string="Sello Compañía")

