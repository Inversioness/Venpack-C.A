/** @odoo-module */

import { Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Payment.prototype, {
    // =========================================================================
    // VALIDACIÓN: ¿Proviene del botón/pop-up de Saldar Cuentas Pendientes?
    // =========================================================================
    _isSaldarCuentaFlow() {
        if (this.pos?.get_order()?.is_saldar_cuenta) {
            return true;
        }

        const modalTitle = document.querySelector('.modal-title, .popup-title');
        if (modalTitle && modalTitle.textContent.toLowerCase().includes('saldar la deuda')) {
            return true;
        }

        return false;
    },

    // =========================================================================
    // 1. TRATAMIENTO DEL MONTO AUTOMÁTICO AL INICIAR (BOTÓN SALDAR DEUDA)
    // =========================================================================
    set_amount(amount) {
        let finalAmount = amount;
        const name = this.payment_method ? this.payment_method.name.toLowerCase() : '';
        let rate = 0;

        if (this._isSaldarCuentaFlow()) {
            
            if (name.includes("usd")) {
                rate = this.pos.config.show_currency_rate;
            } else if (name.includes("eur")) {
                rate = this.pos.config.show_currency2_rate || 0; 
            }

            const bufferState = this.pos.numberBuffer?.state?.buffer || "";
            const isForeignCurrency = name.includes("usd") || name.includes("eur");
            
            if (isForeignCurrency && rate > 0 && rate !== 1 && !this._isConverting && Math.abs(amount) > 0 && bufferState === "") {
                
                finalAmount = amount * rate;
                finalAmount = Math.round((finalAmount + Number.EPSILON) * 100) / 100;

                if (this.pos.numberBuffer && this.pos.numberBuffer.state) {
                    this.pos.numberBuffer.state.buffer = finalAmount.toString();
                }

                this._isConverting = true;
                super.set_amount(finalAmount);
                this._isConverting = false;
                return;
            }
        }

        return super.set_amount(finalAmount);
    },

    // =========================================================================
    // 2. SINCRONIZADOR GRÁFICO (CAPTURA DE TU TECLADO EN USD / EUR)
    // =========================================================================
    _updateLines(buffer) {
        if (this._isSaldarCuentaFlow()) {
            const name = this.payment_method ? this.payment_method.name.toLowerCase() : '';
            const isForeignCurrency = name.includes("usd") || name.includes("eur");
            
            if (isForeignCurrency && buffer !== undefined && buffer !== null) {
                const cleanBuffer = buffer.replace(',', '.');
                const foreignAmountEntered = parseFloat(cleanBuffer);

                if (!isNaN(foreignAmountEntered)) {
                    this.amount = foreignAmountEntered;
                    
                    if (this.pos.numberBuffer?.state) {
                        this.pos.numberBuffer.state.buffer = buffer;
                    }
                    return;
                }
            }
        }

        return super._updateLines(...arguments);
    }
});