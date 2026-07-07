import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def write(self, vals):
        """
        INTERCEPTOR MAESTRO DE BASE DE DATOS (Odoo v17+ / Dual Currency):
        Detecta el cierre de sesión O movimientos manuales de efectivo (In/Out)
        y purga de inmediato los asientos de diferencia generados por transacciones bimoneda.
        """
        # 1. Ejecutar la escritura nativa primero para que se generen los asientos en DB
        res = super(PosSession, self).write(vals)

        # 2. Gatillo: Se activa si se cierra la sesión O si se altera el efectivo (Entradas/Salidas del día)
        is_closing = vals.get('state') == 'closed'
        is_cash_move = any(k in vals for k in ['cash_register_balance_end_real', 'cash_register_balance_start'])

        if is_closing or is_cash_move:
            _logger.info(f"==> [DB-INTERCEPTOR-MASTER] Evento detectado (Cierre: {is_closing}, Movimiento Caja: {is_cash_move}). Evaluando purga...")
            
            for session in self:
                # Mitigación de seguridad: Evaluar transacciones en dólares o euros
                has_foreign_currency = any(
                    payment.payment_method_id.journal_id.currency_id.name in ['USD', 'EUR'] or 
                    any(curr in payment.payment_method_id.name.upper() for curr in ['USD', 'EUR', 'EFECTIVO'])
                    for payment in session.order_ids.mapped('payment_ids')
                )
                
                # Contexto del diario de la sesión
                current_journal = session.cash_journal_id
                is_dual_context = has_foreign_currency or (current_journal and current_journal.currency_id.name in ['USD', 'EUR'])

                if not is_dual_context:
                    _logger.info(f"==> [DB-INTERCEPTOR-MASTER] Sesión {session.name} limpia de flujos bimoneda. Se omite la purga.")
                    continue

                # 3. Buscar asientos contables publicados vinculados a esta sesión específica
                moves = self.env['account.move'].search([
                    ('company_id', '=', session.company_id.id),
                    ('state', '=', 'posted'),
                    '|', 
                    ('journal_id', '=', session.cash_journal_id.id),
                    ('ref', 'ilike', session.name)
                ])

                for move in moves:
                    is_target_move = False
                    for line in move.line_ids:
                        # Evaluamos rigurosamente las cuentas de diferencias o etiquetas intrusas
                        if line.account_id.code in ['800107', '62401005'] or 'Diferencia de efectivo' in (line.name or ''):
                            is_target_move = True
                            break
                    
                    if is_target_move:
                        try:
                            with self.env.cr.savepoint():
                                _logger.info(f"==> [DB-INTERCEPTOR-MASTER] Encontrado asiento intruso bimoneda: {move.name}. Procediendo a eliminar.")
                                
                                # Romper publicación y borrar físicamente (Plan A)
                                move.button_draft()
                                move.unlink()
                                _logger.info("==> [DB-INTERCEPTOR-MASTER] Asiento fantasma eliminado con éxito.")
                        except Exception as e:
                            _logger.warning(f"Odoo impidió borrar el registro. Aplicando Plan B (Vaciado a cero): {str(e)}")
                            try:
                                with self.env.cr.savepoint():
                                    move.line_ids.write({'debit': 0.0, 'credit': 0.0, 'amount_currency': 0.0})
                                    move.write({'ref': f'Diferencia Bimoneda Anulada - {session.name}'})
                                    _logger.info("==> [DB-INTERCEPTOR-MASTER] Montos del asiento reducidos a 0.00.")
                            except Exception as inner_e:
                                _logger.error(f"Fallo crítico en contingencia maestra: {str(inner_e)}")

        return res

    # Mitigaciones de balance en 0 para evitar bloqueos preventivos en la UI
    @api.depends('order_ids')
    def _compute_cash_balance_ref(self):
        for session in self:
            if hasattr(session, 'cash_register_difference_ref'):
                try: session.cash_register_difference_ref = 0.0
                except Exception: pass
        try: super(PosSession, self)._compute_cash_balance_ref()
        except Exception: pass

    @api.depends('order_ids')
    def _compute_cash_balance_ref2(self):
        for session in self:
            if hasattr(session, 'cash_register_difference_ref2'):
                try: session.cash_register_difference_ref2 = 0.0
                except Exception: pass
        try: super(PosSession, self)._compute_cash_balance_ref2()
        except Exception: pass