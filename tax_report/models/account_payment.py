# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
import json
from datetime import datetime
# from odoo.exceptions import ValidationError


class CustomAccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = "Modificar modulo de account payment"

    document_date = fields.Date(string='Fecha Documento')

