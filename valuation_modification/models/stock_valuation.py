from odoo import models, fields, api

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    currency_usd_id = fields.Many2one(
        'res.currency', 
        string='Moneda USD', 
        default=lambda self: self.env.ref('base.USD').id
    )

    total_value_usd = fields.Monetary(
        string='Total USD', 
        compute='_compute_total_value_usd',
        store=True,
        currency_field='currency_usd_id'
    )

    unit_cost_usd = fields.Monetary(
        string='Valor Unitario $', 
        #compute='_compute_valuation_usd',
        currency_field='currency_usd_id',
        #store=True
    )

    @api.depends('quantity', 'unit_cost_usd')
    def _compute_total_value_usd(self):
        for record in self:
            # Usamos 0.0 por defecto para evitar valores nulos en la DB
            record.total_value_usd = (record.quantity or 0.0) * (record.unit_cost_usd or 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product = self.env['product.product'].browse(vals.get('product_id'))
            
            # 1.Si hay un purchase_line_id
            if vals.get('stock_move_id'):
                move = self.env['stock.move'].browse(vals.get('stock_move_id'))
                if move.purchase_line_id:
                    precio_compra = move.purchase_line_id.price_unit
                    vals['unit_cost_usd'] = precio_compra
                    vals['total_value_usd'] = precio_compra * vals.get('quantity', 0.0)
                    continue

            # 2. Si NO es compra, usamos tu variable promedio_usd 
            costo_variable = product.product_tmpl_id.promedio_usd or 0.0
            if costo_variable > 0:
                vals['unit_cost_usd'] = costo_variable
                vals['total_value_usd'] = costo_variable * vals.get('quantity', 0.0)

        return super(StockValuationLayer, self).create(vals_list)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ Este método controla qué números se muestran en las filas grises (agrupaciones) """
        res = super(StockValuationLayer, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)
        
        if 'total_value_usd' in fields:
            for line in res:
                if 'product_id' in line: 
                
                    prod_id = line['product_id'][0] if isinstance(line['product_id'], tuple) else line['product_id']
                    product = self.env['product.product'].browse(prod_id)
                    
                    total_qty = line.get('quantity', 0.0)
                    
                    line['total_value_usd'] = total_qty * (product.promedio_usd or 0.0)
                    
                if 'unit_cost_usd' in fields:
                    if 'product_id' in line:
                        prod_id = line['product_id'][0] if isinstance(line['product_id'], tuple) else line['product_id']
                        product = self.env['product.product'].browse(prod_id)
                        line['unit_cost_usd'] = product.promedio_usd
                    else:
                        line['unit_cost_usd'] = 0.0
        return res

    """@api.depends('value', 'unit_cost', 'account_move_id')
    def _compute_valuation_usd(self):
        for record in self:
            tasa = 0.0
            if record.account_move_id:
                try:
                    self.env.cr.execute(
                        "SELECT x_tasa FROM account_move WHERE id = %s", 
                        (record.account_move_id.id,)
                    )
                    res = self.env.cr.fetchone()
                    tasa = res[0] if res and res[0] else 0.0
                except:
                    tasa = 0.0
            
            if tasa > 0:
                record.total_value_usd = record.value / tasa
                record.unit_cost_usd = record.unit_cost / tasa
            else:
                record.total_value_usd = 0.0
                record.unit_cost_usd = 0.0"""