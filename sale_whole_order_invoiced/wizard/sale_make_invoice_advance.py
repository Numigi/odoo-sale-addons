# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(
        selection_add=[
            ("whole_order", _("Invoice whole order (deduct down payments)"))
        ],
        ondelete={"whole_order": "cascade"},
        default="whole_order",
    )

    def create_invoices(self):
        """Handle the whole_order invoicing option.

        This option creates an invoice the same way as
        `all` / `Invoiceable lines (deduct down payments)`.

        The only difference is that after creating the invoice,
        the sale order is automatically set to invoiced.
        """
        invoice_whole_order = self.advance_payment_method == "whole_order"
        if invoice_whole_order:
            self.advance_payment_method = "delivered"

        res = super().create_invoices()

        if invoice_whole_order:
            sale_orders = self.env["sale.order"].browse(
                self._context.get("active_ids", [])
            )
            sale_orders.write({"whole_order_invoiced": True})

        return res
