# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    show_invoice_email_warning = fields.Boolean(
        compute="_compute_show_invoice_email_warning"
    )

    @api.depends("partner_invoice_id")
    def _compute_show_invoice_email_warning(self):
        for order in self:
            order.show_invoice_email_warning = (
                order.partner_invoice_id and not order.partner_invoice_id.email
            )
