# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PaymentAcquirer(models.Model):

    _inherit = "payment.acquirer"

    auto_confirm_sale_order = fields.Selection(
        [
            ("send_quotation", "Send Quotation"),
            ("confirm_order", "Confirm Order"),
        ],
        string="Automatic Order Confirmation",
    )
