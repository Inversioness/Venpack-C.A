# -*- coding: utf-8 -*-
# Copyright (C) 2021-Today: Part of NextFlowIT. 
# @author:  Part of NextFlowIT. 

from odoo import models, fields, api, _

class ResConfigPosInherit(models.TransientModel):
    _inherit = "res.config.settings"

    nf_pos_enable_discounted_price_on_product = fields.Boolean(related="pos_config_id.nf_pos_enable_discounted_price_on_product", readonly=False)
    nf_pos_enable_dicsounted_price_on_cart = fields.Boolean(related="pos_config_id.nf_pos_enable_dicsounted_price_on_cart", readonly=False)
    nf_pos_enable_discounted_price_in_receipt = fields.Boolean(related="pos_config_id.nf_pos_enable_discounted_price_in_receipt", readonly=False)
    