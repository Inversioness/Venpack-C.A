from odoo import fields, models

class PosSession(models.Model):
    _inherit = "pos.session"

    tax_today = fields.Float(digits=(16,4))
    tax2_today = fields.Float(digits=(16,4))