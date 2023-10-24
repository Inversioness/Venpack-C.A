odoo.define('mai_pos_igtf_de_venezuela.IgtfPaymentScreen', function(require) {
	'use strict';

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');
	const NumberBuffer = require('point_of_sale.NumberBuffer');
	const session = require('web.session');
	var core = require('web.core');
	var _t = core._t;
	// const { onMounted, onWillUnmount } = owl.hooks;

	const IgtfPaymentScreen = PaymentScreen => 
		class extends PaymentScreen {
			constructor() {
				super(...arguments);
		    }

		    async back(){
				let self = this;
				this.currentOrder.removeIGTF();
				self.showScreen('ProductScreen');
			}

			addNewPaymentLine({ detail: paymentMethod }) {
				var self = this;
				var order = this.env.pos.get_order();
				var due = order.get_due();
				// original function: click_paymentmethods
				if (this.currentOrder.electronic_payment_in_progress()) {
					this.showPopup('ErrorPopup', {
						title: this.env._t('Error'),
						body: this.env._t('There is already an electronic payment in progress.'),
					});
					return false;
				}else{
					var payment_method = null;
					var igtf_pay = null;
					for (var i = 0; i < this.env.pos.payment_methods.length; i++ ) {
						if (this.env.pos.payment_methods[i].id === paymentMethod.id ){
							if(this.env.pos.payment_methods[i]['is_igtf'] === true){
								payment_method = this.env.pos.payment_methods[i];
								igtf_pay = true;
								break;
							}else{
								payment_method = this.env.pos.payment_methods[i];
								break;
							}   
						}
					}
					// if(igtf_pay == true && (!order.igtf_charge || order.igtf_charge == 0)){
					if(igtf_pay == true && (order.igtf_charge != due)){
						due = order.get_total_without_igtf() - order.get_total_paid()
						var total  = (self.env.pos.company.igtf_percentage * 0.01 * due ) + order.igtf_charge;
						console.log(this,"due==================",due,total)
						this.env.pos.get_order().set_igtf_charge(total);
						this.currentOrder.add_paymentline(payment_method);
						this.currentOrder.selected_paymentline.set_igtf_amount(total);
						NumberBuffer.reset();
						this.payment_interface = payment_method.payment_terminal;
						if (this.payment_interface) {
							this.currentOrder.selected_paymentline.set_payment_status('pending');
						}
					}else{
						this.currentOrder.add_paymentline(paymentMethod);
						NumberBuffer.reset();
						this.payment_interface = paymentMethod.payment_terminal;
						if (this.payment_interface) {
							this.currentOrder.selected_paymentline.set_payment_status('pending');
						}
					}
					return true;
				}
			}

			deletePaymentLine(event) {
				let self = this;
	            let { cid } = event.detail;
	            let line = this.paymentLines.find((line) => line.cid === cid);
				if(line.is_igtf){
		        	this.currentOrder.set_igtf_charge(0);
		        	if(this.currentOrder.igtf_charge == 0){
		        		this.currentOrder.removeIGTF();
		        	}
		        }
				super.deletePaymentLine(event);
				this.render();
			}

			_updateSelectedPaymentline() {
				let self = this;
				if (this.paymentLines.every((line) => line.paid)) {
					this.currentOrder.add_paymentline(this.payment_methods_from_config[0]);
				}
				if (!this.selectedPaymentLine) return; // do nothing if no selected payment line
				// disable changing amount on paymentlines with running or done payments on a payment terminal
				const payment_terminal = this.selectedPaymentLine.payment_method.payment_terminal;
				if (
					payment_terminal &&
					!['pending', 'retry'].includes(this.selectedPaymentLine.get_payment_status())
				) {
					return;
				}
				if (NumberBuffer.get() === null) {
					this.deletePaymentLine({ detail: { cid: this.selectedPaymentLine.cid } });
				} else {
					if(this.selectedPaymentLine.payment_method.is_igtf){
            			let paymentlines = this.currentOrder.get_paymentlines();
            			let other_line_igtf = 0;
            			for(var id in paymentlines) {
			                var line = paymentlines[id];
			                if(line.cid != this.selectedPaymentLine.cid){
			                	other_line_igtf += line.igtf_amount;
			                }
			            }


						var due = NumberBuffer.getFloat();
						var total  = this.env.pos.company.igtf_percentage * 0.01 * due + other_line_igtf;
						this.env.pos.get_order().set_igtf_charge(total);
						this.selectedPaymentLine.set_igtf_amount(total);
						this.selectedPaymentLine.set_amount(due);
						const igtfProduct = this.env.pos.config.igtf_product_id;
		        		if(igtfProduct){
		        			this.currentOrder.removeIGTF();
			        		this.currentOrder.add_product(this.currentOrder.pos.db.product_by_id[igtfProduct[0]], {
					            quantity: 1,
		              			price: total,
					            lst_price: total,
					        });
					        this.currentOrder.selected_orderline.set_is_igtf_line(true);
		        		}

					}else{
						this.selectedPaymentLine.set_amount(NumberBuffer.getFloat());
					}
				}
			}


		}
	Registries.Component.extend(PaymentScreen, IgtfPaymentScreen);
	return PaymentScreen;

});