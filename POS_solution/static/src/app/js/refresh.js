/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    // El método setup se ejecuta automáticamente siempre que el POS inicia o se refresca
    async setup() {
        await super.setup(...arguments);
        
        console.log("=== [SISTEMA DE LIMPIEZA AUTOMÁTICA DETECTADO] ===");
        this.limpiarPosPorCompleto();
    },

    limpiarPosPorCompleto() {
        console.log("=== [INICIO LIMPIEZA PROFUNDA DE RESIDUOS] ===");

        const order = this.get_order();
        console.log("-> Orden actual en lectura:", order ? order.name : "Ninguna");

        if (order) {
            // 1. Quitar líneas de pago colgadas
            const paymentLines = order.get_paymentlines();
            while (paymentLines.length > 0) {
                console.log(`   X Removiendo línea de pago pegada: ${paymentLines[0].payment_method.name}`);
                order.remove_paymentline(paymentLines[0]);
            }

            // 2. Limpieza forzada del cliente/partner
            if (order.get_partner()) {
                console.log(`   X Desvinculando cliente residual: ${order.get_partner().name}`);
                order.set_partner(null);
                order.partner = null;
            }

            // 3. Romper persistencia local eliminando la orden activa
            console.log("   X Eliminando instancia de orden para purgar el localStorage...");
            this.removeOrder(order);
        }

        // 4. Limpieza manual y directa sobre las llaves del localStorage del navegador
        try {
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && (key.includes("pos_order") || key.includes("orders") || key.includes("active_order"))) {
                    localStorage.removeItem(key);
                }
            }
            console.log("   ✔ LocalStorage higienizado.");
        } catch (e) {
            console.error("!! Error limpiando localStorage:", e);
        }

        // 5. Crear una orden nueva totalmente limpia y anónima
        this.add_new_order();
        const nuevaOrden = this.get_order();
        if (nuevaOrden) {
            nuevaOrden.set_partner(null);
            nuevaOrden.partner = null;
        }

        console.log("=== [FIN LIMPIEZA PROFUNDA: POS HIGIENIZADO] ===");
    }
});