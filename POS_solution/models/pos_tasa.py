# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def load_pos_data(self, *args, **kwargs):
        """
        Valida que tanto la tasa de USD (tax_today) como la de EUR (tax2_today)
        estén alineadas con las tasas oficiales vigentes en contabilidad para el día de hoy.
        """

        loaded_data = super(PosSession, self).load_pos_data()
        
        hoy = fields.Date.today()
        
        for session in self:
            tasa_pos_usd = getattr(session, 'tax_today', 0.0) or 0.0
            tasa_pos_eur = getattr(session, 'tax2_today', 0.0) or 0.0

            # --- PROCESAR TASA CONTABLE USD ---
            usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
            tasa_contable_usd = 0.0
            if usd_currency:
                rate_usd = usd_currency.rate
                if 0 < rate_usd < 1:
                    tasa_contable_usd = round(1 / rate_usd, 4)
                else:
                    tasa_contable_usd = rate_usd

            # --- PROCESAR TASA CONTABLE EUR ---
            eur_currency = self.env['res.currency'].search([('name', '=', 'EUR')], limit=1)
            tasa_contable_eur = 0.0
            if eur_currency:
                rate_eur = eur_currency.rate
                if 0 < rate_eur < 1:
                    tasa_contable_eur = round(1 / rate_eur, 4)
                else:
                    tasa_contable_eur = rate_eur

            # === 🔍 LOGS DE AUDITORÍA EN CONSOLA ===
            #_logger.info("==================================================")
            #_logger.info(">>> AUDITORÍA DE FECHA Y TASAS (USD / EUR) <<<")
            #_logger.info("Sesión: %s | Fecha de Hoy: %s", session.name or 'N/A', hoy)
            #_logger.info("POS - Tasa USD (tax_today): %s | Sistema USD: %s", tasa_pos_usd, tasa_contable_usd)
            #_logger.info("POS - Tasa EUR (tax2_today): %s | Sistema EUR: %s", tasa_pos_eur, tasa_contable_eur)
            #_logger.info("==================================================")

            
            # Control de cambios para el USD
            if tasa_contable_usd > 0 and tasa_pos_usd != tasa_contable_usd:
                raise UserError((
                    "¡Tasa de Cambio Desactualizada (USD)!\n\n"
                    "La tasa de la sesión (%s) no coincide con la tasa oficial establecida "
                    "en Contabilidad para el día de hoy (%s).\n\n"
                    "Por favor, actualice la tasa del Punto de Venta antes de abrir la sesión."
                ) % (tasa_pos_usd, tasa_contable_usd))
                
            # Control de cambios para el EUR
            if tasa_contable_eur > 0 and tasa_pos_eur != tasa_contable_eur:
                raise UserError((
                    "¡Tasa de Cambio Desactualizada (EUR)!\n\n"
                    "La tasa para Euros de la sesión (%s) no coincide con la tasa oficial "
                    "en Contabilidad para el día de hoy (%s).\n\n"
                    "Por favor, actualice la tasa del Punto de Venta antes de abrir la sesión."
                ) % (tasa_pos_eur, tasa_contable_eur))

        return loaded_data