/** @odoo-module **/

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";

// 1. Parcheamos las líneas para que digan que no necesitan lote
patch(Orderline.prototype, {
    has_valid_product_lot() {
        return true;
    },
    get_lot_lines() {
        return [];
    }
});

// 2. Parcheamos la orden completa
patch(Order.prototype, {
    add_orderline(line) {
        const soData = line.sale_order_line_id;
        if (soData) {
            const currentLines = this.get_orderlines();
            const getSoPrefix = (name) => name ? name.split(' - ')[0] : '';
            const incomingPrefix = getSoPrefix(soData.display_name);
            const isDuplicateId = currentLines.some(l => l.sale_order_line_id?.id === soData.id);
            if (isDuplicateId) return;

            if (!this._last_so_load_time) this._last_so_load_time = {};
            const now = Date.now();
            const alreadyHasThisOrder = currentLines.some(l => 
                getSoPrefix(l.sale_order_line_id?.display_name) === incomingPrefix
            );

            if (alreadyHasThisOrder) {
                const lastLoad = this._last_so_load_time[incomingPrefix] || 0;
                const isPartOfSameBatch = (now - lastLoad) < 500;
                if (!isPartOfSameBatch) {
                    if (!this._bloqueo_popup) {
                        this._bloqueo_popup = true;
                        this.pos.env.services.popup.add(ErrorPopup, {
                            title: _t("Pedido ya presente"),
                            body: _t("La cotización " + incomingPrefix + " ya está en el carrito."),
                        });
                        setTimeout(() => { this._bloqueo_popup = false; }, 2000);
                    }
                    return; 
                }
            }
            this._last_so_load_time[incomingPrefix] = now;
            if (soData.product_uom_qty && soData.product_uom_qty > 0) {
                line.set_quantity(soData.product_uom_qty);
            }
        }
        return super.add_orderline(...arguments);
    },

    // Obligamos a la orden a ignorar la validación de lotes
    has_valid_product_lot() {
        return true;
    },

    _can_be_paid() {
        return true;
    }
});