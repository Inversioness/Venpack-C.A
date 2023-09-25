odoo.define('bi_pos_multi_currency.OrderDetailsInherit', function(require) {

	const OrderWidget = require('point_of_sale.OrderWidget');
	const Registries = require('point_of_sale.Registries');

	const session = require('web.session');
	const PosComponent = require('point_of_sale.PosComponent');

	const { useListener } = require('web.custom_hooks');
	let core = require('web.core');
	let _t = core._t;
	const BiOrderWidget = OrderWidget => class extends OrderWidget {
        _updateSummary() {
            let currency = this.env.pos.poscurrency;
            let pos_currency = this.env.pos.currency;
            const total = this.order ? this.order.get_total_with_tax() : 0;
            const tax = this.order ? total - this.order.get_total_without_tax() : 0;
            var all_cur_amount = []
            var all_tax_amount = []
            for(var i=0;i<currency.length;i++)
            {
                if(currency[i].id != pos_currency.id)
                {
                    if(currency[i].name == 'USD' || currency[i].name == 'VES'){
                        let currency_in_pos = (currency[i].rate / this.env.pos.currency.rate);
                        var curr_sym = currency[i].symbol;
                        let curr_tot = total * currency_in_pos;
                        let curr_tax = tax * currency_in_pos; 
                        var main_amount = ""
                        var main_tax = ""
                        if(currency[i].position == 'after'){
                            main_amount = curr_tot.toFixed(currency[i].decimal_places).toString()+ " " +curr_sym  
                            main_tax = curr_tax.toFixed(currency[i].decimal_places).toString()+ " " +curr_sym
                        }else{
                            main_amount = curr_sym + " " + curr_tot.toFixed(currency[i].decimal_places).toString()  
                            main_tax = curr_sym + " " + curr_tax.toFixed(currency[i].decimal_places).toString() 
                        }
                        if(!all_cur_amount.includes(main_amount)){
                             all_cur_amount.push(main_amount)
                        }

                        if(!all_tax_amount.includes(main_tax)){
                             all_tax_amount.push(main_tax)
                        }
                    }
                }else{
                    const formattedUnitPrice = this.env.pos.format_currency(
                        total,
                        'Product Price'
                    );
                    const formattedUnittax = this.env.pos.format_currency(
                        tax,
                        'Product Price'
                    );
                    all_cur_amount.push(formattedUnitPrice)
                    all_tax_amount.push(formattedUnittax)
                }
            }
            this.state.total = all_cur_amount;
            this.state.tax = this.env.pos.format_currency(tax);
            this.render();
        }
	}
	Registries.Component.extend(OrderWidget, BiOrderWidget);

	return OrderWidget;
});