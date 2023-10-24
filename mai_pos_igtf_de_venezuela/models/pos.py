# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class PosPaymentMethod(models.Model):
	_inherit = 'pos.payment.method'

	is_igtf = fields.Boolean("Is IGTF ?")


class AccountBankStatement(models.Model):
	_inherit = 'account.bank.statement'

	igtf_pos_amount = fields.Float("IGTF Amount",compute="_compute_igtf_amt",store=True)

	@api.depends('balance_start','balance_end_real','company_id','pos_session_id')
	def _compute_igtf_amt(self):
		for rec in self:
			rec.igtf_pos_amount = 0
			if rec.pos_session_id :
				rec.igtf_pos_amount = sum(rec.pos_session_id.order_ids.mapped('igtf_amount'))

				
class PosConfig(models.Model):
	_inherit = 'pos.config'

	igtf_product_id = fields.Many2one('product.product',string="Product IGTF ",domain=[('type', '=', 'service'),('available_in_pos','=',True)])


class PosOrder(models.Model):
	_inherit = 'pos.order.line'

	is_igtf_line = fields.Boolean("Is IGTF Line")


class PosOrder(models.Model):
	_inherit = 'pos.order'

	igtf_amount = fields.Float("IGTF Amount",store=True)

	igtf_percentage = fields.Float(string='% IGTF Divisa',related="company_id.igtf_percentage",store=False)
	igtf_payment_method_id = fields.Many2one("pos.payment.method","IGTF Payment Method" ,compute="_compute_pos_igtf_amt",store=False)
	igtf_total_amount = fields.Float("Total Amount + IGTF" ,compute="_compute_pos_igtf_amt",store=False)

	@api.onchange('payment_ids', 'lines')
	def _onchange_amount_all(self):
		for order in self:
			currency = order.pricelist_id.currency_id
			order.amount_paid = sum(payment.amount for payment in order.payment_ids)
			order.amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.payment_ids)
			order.amount_tax = currency.round(sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
			amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
			order.amount_total = order.amount_tax + amount_untaxed + order.igtf_amount

	# @api.depends('igtf_percentage','payment_ids','payment_ids.payment_method_id','payment_ids.payment_method_id','amount_total')
	def _compute_pos_igtf_amt(self):
		for rec in self:
			pay_method = False
			igtf_amount = 0
			igtf_total_amount = 0
			for pl in rec.payment_ids :
				if pl.payment_method_id.is_igtf :
					pay_method = pl.payment_method_id.id
					# igtf_amount += round(rec.igtf_percentage * 0.01 * pl.amount, 2)

			rec.igtf_payment_method_id = pay_method
			# rec.igtf_amount = igtf_amount
			rec.igtf_total_amount = rec.amount_total 

	@api.model
	def _order_fields(self, ui_order):
		for line in ui_order.get('lines',[]) :
			if line[2].get('is_igtf_line') :
				ui_order['lines'].remove(line)

		res = super(PosOrder, self)._order_fields(ui_order)
		res['igtf_amount'] = ui_order.get('igtf_charge') or 0.0
		return res

	def _prepare_igtf_invoice_line(self):
		return {
			'product_id': self.config_id.igtf_product_id.id,
			'quantity': 1,
			'price_unit': self.igtf_amount,
			'name':  'IGTF',
			'tax_ids': [(6, 0,[])],
			'product_uom_id': self.config_id.igtf_product_id.uom_id.id,
		}

	def _prepare_invoice_vals(self):
		res = super(PosOrder, self)._prepare_invoice_vals()
		if self.igtf_amount > 0 :
			line = self._prepare_igtf_invoice_line()
			inv_lines = res.get('invoice_line_ids')
			inv_lines.append((0, None, line))
			res.update({
				'invoice_line_ids' : inv_lines,
				'pos_order_id' : self.id,
			})
		return res

	

class AccountMove(models.Model):
	_inherit = 'account.move'

	pos_order_id = fields.Many2one('pos.order',string="POS order")
	igtf_percentage = fields.Float(string='% IGTF Divisa',related="pos_order_id.igtf_percentage",store=False)
	igtf_payment_method_id = fields.Many2one("pos.payment.method","IGTF Payment Method" ,related="pos_order_id.igtf_payment_method_id",store=False)
	igtf_amount = fields.Float("IGTF Amount" ,related="pos_order_id.igtf_amount",store=False)
	igtf_total_amount = fields.Float("Total Amount + IGTF" ,related="pos_order_id.igtf_total_amount",store=False)


