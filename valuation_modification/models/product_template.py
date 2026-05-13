from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    promedio_usd = fields.Float(
        string='Costo USD', 
        digits=(12, 2),
        default=0.0,
        help="Costo promedio ponderado calculado en USD tras cada recepción de compra."
    )

    def write(self, vals):
       
        res = super(ProductTemplate, self).write(vals)
        
        
        if 'promedio_usd' in vals:
            for record in self:
                nuevo_costo_usd = vals.get('promedio_usd', 0.0)
                if nuevo_costo_usd <= 0 or not record.qty_available:
                    continue
               
                usd_currency = self.env.ref('base.USD')

        return res