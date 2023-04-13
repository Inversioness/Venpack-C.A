odoo.define('bi_pos_multi_currency.biPaymentScreenPaymentLines', function(require) {

	const PaymentScreenPaymentLines = require('point_of_sale.PaymentScreenPaymentLines');
	const Registries = require('point_of_sale.Registries');

	const session = require('web.session');
	const PosComponent = require('point_of_sale.PosComponent');

	const { useListener } = require('web.custom_hooks');
	let core = require('web.core');
	let _t = core._t;
	const biPaymentScreenPaymentLines = PaymentScreenPaymentLines => class extends PaymentScreenPaymentLines {
          formatLineAmount(paymentline) {
            let currency = this.env.pos.poscurrency;
            let pos_currency = this.env.pos.currency;
            var all_cur_amount = []
            const total = paymentline.get_amount()
            for(var i=0;i<currency.length;i++)
            {
                if(currency[i].id != pos_currency.id)
                {
                    if(currency[i].name == 'USD' || currency[i].name == 'VEF'){
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

            console.log("gggggggggggggggggggggggg",all_cur_amount)
            return all_cur_amount;

            // return ;
        }

	}
	Registries.Component.extend(PaymentScreenPaymentLines, biPaymentScreenPaymentLines);

	return PaymentScreenPaymentLines;
});