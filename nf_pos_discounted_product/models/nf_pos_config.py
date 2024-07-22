# -*- coding: utf-8 -*-
# Copyright (C) 2021-Today: Part of NextFlowIT.
# @author:  Part of NextFlowIT.

from odoo import models, fields


class PosConfigModelInherit(models.Model):
    _inherit = "pos.config"

    nf_pos_enable_discounted_price_on_product = fields.Boolean(
        string="Display Base Price on Product")
    nf_pos_enable_dicsounted_price_on_cart = fields.Boolean(
        string="Display Base Price in Cart")
    nf_pos_enable_discounted_price_in_receipt = fields.Boolean(
        string="Display Base Price in Receipt With Stripe")
