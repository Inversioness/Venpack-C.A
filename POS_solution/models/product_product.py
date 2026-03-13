from odoo import models, api

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _get_pos_ui_product_product(self, params):
        
        self.ensure_one()
        
        picking_type = self.config_id.picking_type_id
        
        location_id = picking_type.default_location_src_id.id
        
        products = super()._get_pos_ui_product_product(params)
        
        if location_id:
            product_model = self.env['product.product']
            for product in products:

                product_obj = product_model.browse(product['id'])
                
                stock_en_ubicacion = product_obj.with_context(location=location_id).qty_available
                
                product['qty_available_local'] = stock_en_ubicacion
                
        return products