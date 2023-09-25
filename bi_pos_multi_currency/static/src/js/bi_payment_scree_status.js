odoo.define('bi_pos_multi_currency.BiPaymentScreenStatus', function(require) {

	const PaymentScreenStatus = require('point_of_sale.PaymentScreenStatus');
	const Registries = require('point_of_sale.Registries');

	const session = require('web.session');
	const PosComponent = require('point_of_sale.PosComponent');

	const { useListener } = require('web.custom_hooks');
	let core = require('web.core');
	let _t = core._t;
	const BiPaymentScreenStatus = PaymentScreenStatus => class extends PaymentScreenStatus {
        get changeText() {
            let currency = this.env.pos.poscurrency;
            let pos_currency = this.env.pos.currency;
            var all_cur_amount = []
            const total = this.currentOrder.get_change()
            for(var i=0;i<currency.length;i++)
            {
                if(currency[i].id != pos_currency.id)
                {
                    if(currency[i].name == 'USD' || currency[i].name == 'VES'){
                        let currency_in_pos = (currency[i].rate / this.env.pos.currency.rate);
                        var curr_sym = currency[i].symbol;
                        let curr_tot = total * currency_in_pos;
                        var main_amount = ""
                        if(currency[i].position == 'after'){
                            main_amount = curr_tot.toFixed(currency[i].decimal_places).toString()+ " " +curr_sym  
                        }else{
                            main_amount = curr_sym + " " + curr_tot.toFixed(currency[i].decimal_places).toString()  
                        }
                        if(!all_cur_amount.includes(main_amount)){
                             all_cur_amount.push(main_amount)
                        }
                    }
                }else{
                    all_cur_amount.push(this.env.pos.format_currency(this.currentOrder.get_change()))
                }
            }

            console.log("gggggggggggggggggggggggg",all_cur_amount)
            return all_cur_amount;
        }
        get totalDueText() {

            let currency = this.env.pos.poscurrency;
            let pos_currency = this.env.pos.currency;
            var all_cur_amount = []
            const total = this.currentOrder.get_total_with_tax() + this.currentOrder.get_rounding_applied()
            for(var i=0;i<currency.length;i++)
            {
                if(currency[i].id != pos_currency.id)
                {
                    if(currency[i].name == 'USD' || currency[i].name == 'VES'){
                        let currency_in_pos = (currency[i].rate / this.env.pos.currency.rate);
                        var curr_sym = currency[i].symbol;
                        let curr_tot = total * currency_in_pos;
                        var main_amount = ""
                        if(currency[i].position == 'after'){
                            main_amount = curr_tot.toFixed(currency[i].decimal_places).toString()+ " " +curr_sym  
                        }else{
                            main_amount = curr_sym + " " + curr_tot.toFixed(currency[i].decimal_places).toString()  
                        }
                        if(!all_cur_amount.includes(main_amount)){
                             all_cur_amount.push(main_amount)
                        }
                    }
                }else{
                    all_cur_amount.push(this.env.pos.format_currency(total))
                }
            }

            console.log("aaaaaaaaaaaaaaaaaaaaaaa",all_cur_amount)
            return all_cur_amount;

            // return this.env.pos.format_currency(
            //     this.currentOrder.get_total_with_tax() + this.currentOrder.get_rounding_applied()
            // );
        }
        get remainingText() {
            let currency = this.env.pos.poscurrency;
            let pos_currency = this.env.pos.currency;
            var all_cur_amount = []
            const total =  this.currentOrder.get_due() > 0 ? this.currentOrder.get_due() : 0
            for(var i=0;i<currency.length;i++)
            {
                if(currency[i].id != pos_currency.id)
                {
                    if(currency[i].name == 'USD' || currency[i].name == 'VES'){
                        let currency_in_pos = (currency[i].rate / this.env.pos.currency.rate);
                        var curr_sym = currency[i].symbol;
                        let curr_tot = total * currency_in_pos;
                        var main_amount = ""
                        if(currency[i].position == 'after'){
                            main_amount = curr_tot.toFixed(currency[i].decimal_places).toString()+ " " +curr_sym  
                        }else{
                            main_amount = curr_sym + " " + curr_tot.toFixed(currency[i].decimal_places).toString()  
                        }
                        if(!all_cur_amount.includes(main_amount)){
                             all_cur_amount.push(main_amount)
                        }
                    }
                }else{
                    all_cur_amount.push(this.env.pos.format_currency(total))
                }
            }

            console.log("awwwwwwwwwwwwwwwwwwwww",all_cur_amount)
            return all_cur_amount;

            // return this.env.pos.format_currency(
            //     this.currentOrder.get_due() > 0 ? this.currentOrder.get_due() : 0
            // );
        }
        get currentOrder() {
            return this.env.pos.get_order();
        }

	}
	Registries.Component.extend(PaymentScreenStatus, BiPaymentScreenStatus);

	return PaymentScreenStatus;
});