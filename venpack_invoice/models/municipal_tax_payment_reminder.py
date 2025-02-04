import logging
import base64
from odoo import models, fields, api
from datetime import timedelta

_logger = logging.getLogger(__name__)


class MunicipalTaxPaymentReminder(models.Model):
    _name = "municipal.tax.payment.reminder"
    _description = (
        "Lógica para enviar recordatorios por correo de impuestos municipales"
    )

    @api.model
    def _send_municipal_tax_list_to_suppliers(self):
        # Obtener la fecha actual del sistema
        current_date = fields.Date.context_today(self)
        yesterday = current_date - timedelta(days=1)

        company_ids = self.env['res.company'].search([
            ('email', '!=', False)
        ]).mapped('id')

        # Filtrar las facturas no pagadas
        unpaid_tax_invoices = self.env["account.move"].sudo().search(
            [
                ("state", "=", "posted"),
                ("company_id", "in", company_ids),
                ("move_type", "in", ["in_invoice", "in_refund"]),
                ("date", "=", yesterday),
            ]
        )
        if unpaid_tax_invoices:
            for invoice in unpaid_tax_invoices:
                if (
                    invoice.partner_id.automatic_municipal_retention_sending
                    and invoice.partner_id.email
                ):
                # if (invoice.partner_id.email):
                    report_attachment_ids = []
                    for tax in invoice.tax_totals["groups_by_subtotal"]["Base imponible"]:
                        if "Retención Mcpal." in tax["tax_group_name"]:
                            invoice_report = self.env.ref("venpack_invoice.municipal_taxes_report")
                            generated_report = (
                                self.env["ir.actions.report"]
                                .sudo()
                                ._render_qweb_pdf(invoice_report, [invoice.id], data=None)
                            )
                            data_record = base64.b64encode(generated_report[0])
                            account_ref = "_" + invoice.ref if invoice.ref else ""
                            ir_values = {
                                "name": "Comprobante_ISAE" + account_ref,
                                "type": "binary",
                                "datas": data_record,
                                "store_fname": data_record,
                                "mimetype": "application/pdf",
                                "res_model": "account.move",
                            }
                            invoice_report_attachment_id = (
                                self.env["ir.attachment"].sudo().create(ir_values)
                            )
                            report_attachment_ids.append(invoice_report_attachment_id.id)

                    if report_attachment_ids:
                        email_template = self.env.ref(
                            "venpack_invoice.email_template_municipal_tax_list_to_suppliers"
                        )
                        if email_template:
                            email_template["attachment_ids"] = [
                                (6, 0, report_attachment_ids)
                            ]
                            email_template.send_mail(invoice.id, force_send=True)
                            email_template["attachment_ids"] = [(5, 0, 0)]
