odoo.define('bi_pos_multi_currency.BiPaymentItems', function(require) {

	const ProductItem = require('point_of_sale.ProductItem');
	const Registries = require('point_of_sale.Registries');

	const session = require('web.session');
	const PosComponent = require('point_of_sale.PosComponent');

	const { useListener } = require('web.custom_hooks');
	let core = require('web.core');
	let _t = core._t;

	const BiPaymentItems = ProductItem => class extends ProductItem {
        get price() {
            let currency = this.env.pos.poscurrency;
            let pos_currency = this.env.pos.currency;
            const formattedUnitPrice = this.env.pos.format_currency(
                this.props.product.get_price(this.pricelist, 1),
                'Product Price'
            );
            var all_cur_amount = []
            for(var i=0;i<currency.length;i++)
            {
                if(currency[i].id != pos_currency.id)
                {
                    if(currency[i].name == 'USD' || currency[i].name == 'VES'){
                        let currency_in_pos = (currency[i].rate / this.env.pos.currency.rate);
                        var curr_sym = currency[i].symbol;
                        let curr_tot =this.props.product.get_price(this.pricelist, 1)*currency_in_pos;
                        var main_amount = ""
                        if(currency[i].position == 'after'){
                            main_amount = curr_tot.toFixed(currency[i].decimal_places).toString()+ " " +curr_sym  
                        }else{
                            main_amount = curr_sym +" " + curr_tot.toFixed(currency[i].decimal_places).toString()  
                        }
                        if(!all_cur_amount.includes(main_amount)){
                            if (this.props.product.to_weight) {
                                var update_weight =  `${main_amount}/${
                                    this.env.pos.units_by_id[this.props.product.uom_id[0]].name
                                }`;
                                all_cur_amount.push(update_weight)
                            } else {
                                 all_cur_amount.push(main_amount)
                            }
                        }
                    }
                }else{
                    if(!all_cur_amount.includes(formattedUnitPrice)){
                        if (this.props.product.to_weight) {
                            var update_weight =  `${formattedUnitPrice}/${
                                this.env.pos.units_by_id[this.props.product.uom_id[0]].name
                            }`;
                            all_cur_amount.push(update_weight)
                        } else {
                             all_cur_amount.push(formattedUnitPrice)
                        }
                    }
                }
            }
            return all_cur_amount
        }
	}
	Registries.Component.extend(ProductItem, BiPaymentItems);

	return ProductItem;
});