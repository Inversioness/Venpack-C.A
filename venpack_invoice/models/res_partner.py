# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _


class CustomResPartner(models.Model):
    _inherit = 'res.partner'
    _description = "Modificar modulo de res partner"

    x_patent_number = fields.Char(string='No Patente', default=False)
    automatic_municipal_retention_sending = fields.Boolean(string='Envío automático de retenciones municipales', default=False)
