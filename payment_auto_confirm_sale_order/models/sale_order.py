# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_payment_transaction(self, vals):
        transaction = super()._create_payment_transaction(vals)
        action = transaction.acquirer_id.auto_confirm_sale_order
        if action == "confirm_order":
            self.with_context(send_email=True).action_confirm()
        elif action == "send_quotation":
            email_act = self[0].action_quotation_send()
            if email_act and email_act.get("context"):
                email_ctx = email_act["context"]
                email_ctx.update(default_email_from=self[0].company_id.email)
                self.with_context(**email_ctx).message_post_with_template(
                    email_ctx.get("default_template_id")
                )

        return transaction
