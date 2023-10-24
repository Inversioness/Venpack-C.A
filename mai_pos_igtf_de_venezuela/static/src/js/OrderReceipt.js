odoo.define('mai_pos_igtf_de_venezuela.IgtfOrderReceipt', function(require) {
	'use strict';

	const OrderReceipt = require('point_of_sale.OrderReceipt');
	const Registries = require('point_of_sale.Registries');
	const NumberBuffer = require('point_of_sale.NumberBuffer');
	const session = require('web.session');
	var core = require('web.core');
	var _t = core._t;
	// const { onMounted, onWillUnmount } = owl.hooks;

	const IgtfOrderReceipt = OrderReceipt => 
		class extends OrderReceipt {
			constructor() {
				super(...arguments);
		    }

		    get receipt() {
            	return this.receiptEnv.receipt;
        	}

		}
	Registries.Component.extend(OrderReceipt, IgtfOrderReceipt);
	return OrderReceipt;

});