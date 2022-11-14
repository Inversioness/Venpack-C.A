# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
from odoo.tools import remove_accents
import logging
import re

_logger = logging.getLogger(__name__)

class CustomAccountJournal(models.Model):
    _inherit = "account.journal"
    _description = "Custom Journal"

    tax_code = fields.Char(string='Codigo de Impuesto')
