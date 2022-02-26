# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    return_rate = fields.Char(
        compute="_compute_return_rate", string="Return", store=True
    )

    def _compute_return_rate(self):
        for order in self:
            order.return_rate = order._get_return_rate()

    def _get_return_rate(self):
        lines_without_services = self.order_line.filtered(
            lambda l: l.product_id.type in ("product", "consu")
        )
        returned = sum(lines_without_services.mapped(lambda l: l.rental_returned_qty))
        total_qty = sum(lines_without_services.mapped(lambda l: l.product_uom_qty))
        completion = (returned / total_qty) if total_qty else 1
        return "{}%".format(int(completion * 100))
