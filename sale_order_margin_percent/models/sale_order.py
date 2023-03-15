# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin_percent = fields.Float(
        string="Margin Percentage",
        compute="_compute_margin_percent",
        store=True,
    )

    @api.depends("order_line.margin", "order_line.price_subtotal")
    def _compute_margin_percent(self):
        for order in self:
            total_margin = sum(order.order_line.mapped("margin"))
            total_price = sum(order.order_line.mapped("price_subtotal"))
            order.margin_percent = total_margin / total_price if total_price else None
