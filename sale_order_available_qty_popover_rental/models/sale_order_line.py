# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    available_qty_for_popover = fields.Float(
        compute="_compute_available_qty_for_popover_rental"
    )

    @api.depends("product_id")
    def _compute_available_qty_for_popover_rental(self):
        qty = 0
        stock_qty_obj = self.env["stock.quant"]
        for line in self:
            if line.order_id.is_rental:
                stock_qty_lines = stock_qty_obj.search(
                    [
                        ("product_id", "=", self.product_id.id),
                        ("location_id.is_rental_stock_location", "=", True),
                    ]
                )
                for raw in stock_qty_lines:
                    if raw.quantity > 0:
                        qty += raw.quantity
                line.available_qty_for_popover = qty
            else:
                stock_qty_lines = stock_qty_obj.search(
                    [
                        ("product_id", "=", self.product_id.id),
                        ("location_id.is_rental_stock_location", "=", False),
                    ]
                )
                for raw in stock_qty_lines:
                    if raw.quantity > 0:
                        qty += raw.quantity
                line.available_qty_for_popover = qty
