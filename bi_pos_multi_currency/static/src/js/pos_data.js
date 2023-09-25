odoo.define('bi_pos_currency_rate.pos_data', function (require) {
"use strict";

var models = require('point_of_sale.models');
let core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;

	// models.load_fields('product.product', ['list_price' , 'x_studio_precio_ventas_usd']);

	models.load_models({
		model: 'res.currency',
		fields: ['name','symbol','position','rounding','rate','rate_in_company_currency','decimal_places'],
		domain: null, 
		loaded: function(self, poscurrency){
			self.poscurrency = poscurrency;
		},
	});

	var OrderSuper = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attributes, options) {
			OrderSuper.initialize.apply(this, arguments);
			this.currency_amount = this.currency_amount || "";
			this.currency_symbol = this.currency_symbol || "";
			this.currency_name = this.currency_name || "";
			this.recipet = this.recipet || "";
		},

		set_symbol: function(currency_symbol){
			this.currency_symbol = currency_symbol;
			this.trigger('change',this);
		},

		set_curamount: function(currency_amount){
			this.currency_amount = currency_amount;
			this.trigger('change',this);
		},

		set_curname: function(currency_name){
			this.currency_name = currency_name;
			this.trigger('change',this);
		},

		set_inrecipt: function(recipet){
			this.recipet = recipet;
			this.trigger('change',this);
		},

		get_curamount: function(currency_amount){
			return this.currency_amount;
		},

		get_symbol: function(currency_symbol){
			return this.currency_symbol;
		},

		get_curname: function(currency_name){
			return this.currency_name;
		},

		get_inrecipt: function(recipet){
			return this.recipet;
		},

	   export_for_printing: function(){
            var json = OrderSuper.export_for_printing.call(this);
			json.currency_amount = this.get_curamount() || 0.0;
			json.currency_symbol = this.get_symbol() || false;
			json.currency_name = this.get_curname() || false;
			json.recipet = this.get_inrecipt()|| false;
            return json;
        },


		export_as_JSON: function() {
			var self = this;
			var loaded = OrderSuper.export_as_JSON.apply(this, arguments);
			loaded.currency_amount = self.get_curamount() || 0.0;
			loaded.currency_symbol = self.get_symbol() || false;
			loaded.currency_name = self.get_curname() || false;
			loaded.recipet = self.get_inrecipt()|| false;
			return loaded;
		},

		init_from_JSON: function(json){
			OrderSuper.init_from_JSON.apply(this,arguments);
			this.currency_amount = json.currency_amount || "";
			this.currency_symbol = json.currency_symbol || "";
			this.currency_name = json.currency_name || "";
			this.recipet = json.recipet || "";
		},

	});

	var PaymentSuper = models.Paymentline.prototype;
	models.Paymentline = models.Paymentline.extend({
		initialize: function(attributes, options) {
			PaymentSuper.initialize.apply(this, arguments);
			this.currency_amount = this.currency_amount || "";
			this.currency_name = this.currency_name || "";
		},

		export_as_JSON: function() {
			var self = this;
			var loaded = PaymentSuper.export_as_JSON.apply(this, arguments);
			loaded.currency_amount = this.order.currency_amount || 0.0;
			loaded.currency_name = this.order.currency_name || false;
			return loaded;
		},

		init_from_JSON: function(json){
			PaymentSuper.init_from_JSON.apply(this,arguments);
			this.currency_amount = json.currency_amount || "";
			this.currency_name = json.currency_name || "";
		},
	});

	var OrderlineSuper = models.Orderline.prototype;
	models.Orderline = models.Orderline.extend({
		get_other_unit_price : function(){
			var unit_price = this.get_unit_display_price()
            let currency = this.pos.poscurrency;
            let pos_currency = this.pos.currency;
			var other_prices = []
              for(var i=0;i<currency.length;i++)
            {
                if(currency[i].id != pos_currency.id)
                {
                    if(currency[i].name == 'USD' || currency[i].name == 'VES'){
                        let currency_in_pos = (currency[i].rate/this.pos.currency.rate);
                        var curr_sym = currency[i].symbol;
                        let curr_tot =unit_price*currency_in_pos;
                        var main_amount = ""
                        if(currency[i].position == 'after'){
                            main_amount = curr_tot.toFixed(currency[i].decimal_places).toString()+ " " +curr_sym  
                        }else{
                            main_amount = curr_sym +" " + curr_tot.toFixed(currency[i].decimal_places).toString()  
                        }
                       	other_prices.push(main_amount)
                            
                    }
                }else{
                    const formattedUnitPrice = this.pos.format_currency(
                        unit_price,
                        'Product Price'
                    );
                    other_prices.push(formattedUnitPrice)
                }
            }
            return other_prices
		},
		get_other_currency : function(){
			var base_price = this.get_display_price()
            let currency = this.pos.poscurrency;
            let pos_currency = this.pos.currency;
			var other_prices = []
            for(var i=0;i<currency.length;i++)
            {
                if(currency[i].id != pos_currency.id)
                {
                    if(currency[i].name == 'USD' || currency[i].name == 'VES'){
                        let currency_in_pos = (currency[i].rate/this.pos.currency.rate);
                        var curr_sym = currency[i].symbol;
                        let curr_tot =base_price*currency_in_pos;
                        var main_amount = ""
                        if(currency[i].position == 'after'){
                            main_amount = curr_tot.toFixed(currency[i].decimal_places).toString()+ " " +curr_sym  
                        }else{
                            main_amount = curr_sym +" " + curr_tot.toFixed(currency[i].decimal_places).toString()  
                        }
                       	other_prices.push(main_amount)
                            
                    }
                }else{
                    const formattedUnitPrice = this.pos.format_currency(
                        base_price,
                        'Product Price'
                    );
                    other_prices.push(formattedUnitPrice)
                }
            }
            return other_prices
		}
	});

});
