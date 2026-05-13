from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        # 1. Validación original
        res = super(StockPicking, self).button_validate()

        if res is True and self.picking_type_id.code == 'incoming':
            for line in self.move_ids_without_package:
                product = line.product_id
                purchase_line = line.purchase_line_id
                
                if not purchase_line or not product:
                    continue

                # --- CÁLCULO DEL COSTO DE ESTA COMPRA ---
                precio_unitario = purchase_line.price_unit or 0.0
                orden = purchase_line.order_id
                
                if orden.currency_id.name == 'VES':
                    tasa = getattr(orden, 'x_tasac', 0.0)
                    costo_compra_usd = precio_unitario / tasa if tasa > 1 else precio_unitario
                else:
                    costo_compra_usd = precio_unitario

                # ---FÓRMULA DE PROMEDIO PONDERADO ---
                cant_recibida = getattr(line, 'quantity', 0.0) or getattr(line, 'quantity_done', 0.0)
                
                costo_anterior_usd = product.promedio_usd or 0.0
                
                stock_previo = product.qty_available - cant_recibida
                total_stock_final = stock_previo + cant_recibida

                if total_stock_final > 0:
                    stock_calc = max(stock_previo, 0)
                    
                    nuevo_promedio = ((stock_calc * costo_anterior_usd) + 
                                     (cant_recibida * costo_compra_usd)) / total_stock_final
                    
                    product.write({
                        'promedio_usd': nuevo_promedio
                    })
        
        return res