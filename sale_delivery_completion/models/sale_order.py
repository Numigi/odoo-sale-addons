# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    completion_rate = fields.Char(compute="_compute_completion_rate", store=True)

    def _compute_completion_rate(self):
        for order in self:
            order.completion_rate = order._get_completion_rate()

    def _get_completion_rate(self):
        lines_without_services = self.order_line.filtered(
            lambda l: l.product_id.type in ("product", "consu")
        )
        delivered = sum(lines_without_services.mapped(lambda l: l.qty_delivered))
        total_qty = sum(lines_without_services.mapped(lambda l: l.product_uom_qty))
        completion = (delivered / total_qty) if total_qty else 1
        return "{}%".format(int(completion * 100))
