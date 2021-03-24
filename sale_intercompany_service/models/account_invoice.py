# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    interco_service_order_id = fields.Many2one("sale.order", ondelete="restrict")
    interco_customer_invoice_id = fields.Many2one(
        "account.invoice", ondelete="restrict"
    )
    interco_supplier_invoice_id = fields.Many2one(
        "account.invoice", ondelete="restrict"
    )
    is_interco_service = fields.Boolean()

    def open_interco_service_summary(self):
        order = self.sudo().interco_service_order_id
        wizard = self.env["sale.interco.service.invoice"].create(
            {"order_id": order.id, "mode": "summary"}
        )
        action = wizard.get_formview_action()
        action["name"] = _("Interco Service")
        view_ref = (
            "seller_wizard" if self.company_id == order.company_id else "buyer_wizard"
        )
        action["views"] = [
            (self.env.ref(f"sale_intercompany_service.{view_ref}").id, "form")
        ]
        action["target"] = "new"
        return action
