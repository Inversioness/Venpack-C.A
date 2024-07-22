odoo.define('nf_pos_discounted_product.nf_pos_custom', function(require) {
    'use strict';

    var { PosGlobalState, Orderline } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const NfdiscountOrderLine = (Orderline) => class NfdiscountOrderLine extends Orderline {
        
        export_for_printing() {
            var lines = super.export_for_printing();
            lines['product'] = this.get_product()
            lines['price_extra'] = this.price_extra
            var sale_price = this.get_lst_price();
            var offer_price = this.get_unit_price();
    
            var total_disc = ((sale_price - offer_price) / sale_price * 100).toFixed(2)
            if (this.pos.config.nf_pos_enable_discounted_price_in_receipt) {
                if (total_disc < 100 && total_disc > 0) {
                    lines['custom_discount'] = total_disc;
                }
            }
            return lines
        }
        
    }
   
    Registries.Model.extend(Orderline, NfdiscountOrderLine);


});