odoo.define('mai_pos_igtf_de_venezuela.pos', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.ProductScreen');
	var core = require('web.core');
	const { Gui } = require('point_of_sale.Gui');
	var popups = require('point_of_sale.ConfirmPopup');
	var QWeb = core.qweb;
	var utils = require('web.utils');
	var round_pr = utils.round_precision;
	var _t = core._t;

	models.load_fields('res.company', ['is_igtf','igtf_percentage'])
	models.load_fields('pos.payment.method', ['is_igtf'])

	var OrderSuper = models.Order.prototype;
	models.Order = models.Order.extend({

		init: function(parent, options) {
			var self = this;
			this._super(parent,options);
			this.igtf_charge = this.igtf_charge || 0;
			this.set_igtf_charge(this.igtf_charge);
		},

		removeIGTF: function(){
        	this.orderlines
            .filter(({ is_igtf_line }) => is_igtf_line)
            .forEach((line) => this.remove_orderline(line));
    	},

		set_igtf_charge: function(entered_charge){
			this.igtf_charge = entered_charge;
			this.trigger('change',this);
		},

		get_igtf_charge: function(){
			var self = this;
			return this.igtf_charge || 0;
		},

		get_total_with_igtf: function() {
			return this.get_total_with_tax() ;
		},

		get_total_without_igtf: function(){
			var self = this;
			return round_pr(this.orderlines.reduce((function(sum, orderLine) {
				if(orderLine.is_igtf_line == false){
	            	return sum + orderLine.get_price_with_tax();
				}else{
					return sum
				}
	        }), 0), this.pos.currency.rounding);
		},

		add_paymentline: function(payment_method) {
			this.assert_editable();
			if (this.electronic_payment_in_progress()) {
				return false;
			} else {
				var newPaymentline = new models.Paymentline({},{order: this, payment_method:payment_method, pos: this.pos});

				var igtf = this.get_igtf_charge();
				var due = this.get_due() ;

				newPaymentline.set_amount(due);
				
				if(payment_method.is_igtf){
					newPaymentline.set_is_igtf(true);
				}
				this.paymentlines.add(newPaymentline);
				this.select_paymentline(newPaymentline);
				if(this.pos.config.cash_rounding){
					this.selected_paymentline.set_amount(0);
			 		this.selected_paymentline.set_amount(due);
				}

				if (payment_method.payment_terminal) {
					newPaymentline.set_payment_status('pending');
				}

				const igtfProduct = this.pos.config.igtf_product_id;
        		if(igtfProduct){
        			this.removeIGTF();
	        		this.add_product(this.pos.db.product_by_id[igtfProduct[0]], {
			            quantity: 1,
              			price: igtf,
			            lst_price: igtf,
			        });
			        this.selected_orderline.set_is_igtf_line(true)
        		}

				return newPaymentline;
			}
		},
	
		export_as_JSON: function() {
			var self = this;
			var loaded = OrderSuper.export_as_JSON.call(this);
			loaded.igtf_charge = self.get_igtf_charge() || 0;
			loaded.amount_total =self.get_total_with_tax() ;
			return loaded;
		},

		init_from_JSON: function(json){
			OrderSuper.init_from_JSON.apply(this,arguments);
			this.igtf_charge = json.igtf_charge || 0.0;
			this.amount_total = json.amount_total || 0.0;
		},

		export_for_printing: function() {
			var self = this;
			var orderlines = [];
			var loaded = OrderSuper.export_for_printing.call(this);
	        this.orderlines.each(function(orderline){
	        	if(!orderline.is_igtf_line){
	            	orderlines.push(orderline.export_for_printing());
	        	}
	        });
			loaded.orderlines = orderlines;
			return loaded;
		},


	
	});

	var _super_orderline = models.Orderline.prototype;
	models.Orderline = models.Orderline.extend({
	    initialize: function(attr, options) {
	        _super_orderline.initialize.call(this,attr,options);
	        this.is_igtf_line = this.is_igtf_line || "";
	    },
	    set_is_igtf_line: function(is_igtf_line){
	        this.is_igtf_line = is_igtf_line;
	        this.trigger('change',this);
	    },
	    get_is_igtf_line: function(is_igtf_line){
	        return this.is_igtf_line;
	    },
	    can_be_merged_with: function(orderline) {
	        if (orderline.get_is_igtf_line() !== this.get_is_igtf_line()) {
	            return false;
	        } else {
	            return _super_orderline.can_be_merged_with.apply(this,arguments);
	        }
	    },
	    clone: function(){
	        var orderline = _super_orderline.clone.call(this);
	        orderline.is_igtf_line = this.is_igtf_line;
	        return orderline;
	    },
	    export_as_JSON: function(){
	        var json = _super_orderline.export_as_JSON.call(this);
	        json.is_igtf_line = this.is_igtf_line;
	        return json;
	    },
	    init_from_JSON: function(json){
	        _super_orderline.init_from_JSON.apply(this,arguments);
	        this.is_igtf_line = json.is_igtf_line;
	    },
	});

	var PaymentSuper = models.Paymentline;
	models.Paymentline = models.Paymentline.extend({
		init: function(parent,options){
			this._super(parent,options);
			this.is_igtf = this.is_igtf || "";
			this.igtf_amount = this.igtf_amount || 0 ;
		},

		export_as_JSON: function() {
			var self = this;
			var loaded = PaymentSuper.prototype.export_as_JSON.call(this);
			loaded.is_igtf = this.is_igtf || "";
			loaded.igtf_amount = this.igtf_amount || 0 ;
			return loaded;
		},

		init_from_JSON: function(json){
			PaymentSuper.prototype.init_from_JSON.apply(this,arguments);
			this.is_igtf = json.is_igtf || "";
			this.igtf_amount = json.igtf_amount || 0 ;
		},

		set_is_igtf: function(is_igtf){
			this.is_igtf = is_igtf;
			this.trigger('change',this);
		},

		get_is_igtf: function(){
			return this.is_igtf;
		},

		set_igtf_amount: function(igtf_amount){
			this.igtf_amount = igtf_amount;
			this.trigger('change',this);
		},

		get_igtf_amount: function(){
			return this.igtf_amount;
		},

	});


});
