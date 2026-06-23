/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { floatIsZero } from "@web/core/utils/numbers";

patch(PaymentScreen.prototype, {
    // =========================================================================
    // VALIDACIÓN DINÁMICA EXCLUSIVA PARA FLUJO DE COBRANZA (SALDAR CUENTAS)
    // =========================================================================
    async validateOrder(isForceValidate) {
        const order = this.currentOrder;
        const partner = order ? order.get_partner() : null;
        
        const orderLines = order ? order.get_orderlines() : [];
        const totalOrdenOriginalBs = order ? order.get_total_with_tax() : 0;

        const esFlujoCobranzaPura = partner && 
                                    floatIsZero(totalOrdenOriginalBs, this.pos.currency.decimal_places) && 
                                    orderLines.length <= 1;

        if (esFlujoCobranzaPura) {
            //console.log("=== [MODO COBRANZA DETECTADO] Ejecutando lógica de Abonos/Anticipos ===");

            const paylaterPaymentMethod = this.pos.payment_methods.find(
                (method) => this.pos.config.payment_method_ids.includes(method.id) && method.type == "pay_later"
            );

            if (!paylaterPaymentMethod) {
                console.error("=== [COBRANZA] Error: Falta configurar el método 'pay_later' ===");
                return super.validateOrder(...arguments);
            }

            let rate = this.pos.config.show_currency_rate || 0;
            let simboloDivisa = 'USD';
            let formatoLocal = 'en-US';

            const paymentLines = order ? order.get_paymentlines() : [];
            const tienePagoEur = paymentLines.some(line => line.payment_method && line.payment_method.name.toLowerCase().includes("eur"));

            if (tienePagoEur) {
                rate = this.pos.config.show_currency2_rate || 0;
                simboloDivisa = 'EUR';
                formatoLocal = 'de-DE';
            }

            const totalAbonoBs = order.get_total_paid();
            const deudaClienteRealBs = partner.total_due || 0;

            if (totalAbonoBs > 0) {
                let abonoVisualDivisa = totalAbonoBs;
                if (rate > 0 && rate !== 1) {
                    abonoVisualDivisa = Math.round((totalAbonoBs * rate + Number.EPSILON) * 100) / 100;
                }
                const formattedAbonoDivisa = abonoVisualDivisa.toLocaleString(formatoLocal, { style: 'currency', currency: simboloDivisa });

                if (totalAbonoBs < deudaClienteRealBs) {
                    
                    const { confirmed } = await this.popup.add(ConfirmPopup, {
                        title: _t("Confirmación de Abono Parcial"),
                        body: _t("¿Desea registrar un abono parcial de %s a la cuenta de %s? Su deuda disminuirá.", formattedAbonoDivisa, partner.name),
                        confirmText: _t("Confirmar Abono"),
                        cancelText: _t("Cancelar"),
                    });

                    if (confirmed) {
                        const montoPuntoBridge = -totalAbonoBs;
                        const paylaterPayment = order.add_paymentline(paylaterPaymentMethod);
                        paylaterPayment.set_amount(montoPuntoBridge);
                        
                        console.log(`[ABONO PARCIAL] Aplicado contraasiento negativo de: ${montoPuntoBridge} Bs`);
                        return super.validateOrder(...arguments);
                    } else {
                        return;
                    }
                } 
                
                else {
                    const saldoAFavorBs = Math.round((totalAbonoBs - deudaClienteRealBs + Number.EPSILON) * 100) / 100;
                    
                    let favorVisualDivisa = saldoAFavorBs;
                    if (rate > 0 && rate !== 1) {
                        favorVisualDivisa = Math.round((saldoAFavorBs * rate + Number.EPSILON) * 100) / 100;
                    }
                    const formattedFavorDivisa = favorVisualDivisa.toLocaleString(formatoLocal, { style: 'currency', currency: simboloDivisa });

                    const msgBody = deudaClienteRealBs === 0 
                        ? _t("El cliente no posee deuda. ¿Desea registrar un saldo a favor (Anticipo) por %s para %s?", formattedAbonoDivisa, partner.name)
                        : _t("El abono supera la deuda. Se pagarán los %s Bs pendientes y el cliente quedará con un saldo a favor de %s.", deudaClienteRealBs, formattedFavorDivisa);

                    const { confirmed } = await this.popup.add(ConfirmPopup, {
                        title: _t("Registro de Saldo a Favor"),
                        body: msgBody,
                        confirmText: _t("Registrar Anticipo"),
                        cancelText: _t("Cancelar"),
                    });

                    if (confirmed) {
                        const montoPuntoBridge = -totalAbonoBs; 
                        const paylaterPayment = order.add_paymentline(paylaterPaymentMethod);
                        paylaterPayment.set_amount(montoPuntoBridge);

                        return super.validateOrder(...arguments);
                    } else {
                        return;
                    }
                }
            }
        }

        return super.validateOrder(...arguments);
    }
});