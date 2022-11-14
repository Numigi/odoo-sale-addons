# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

GREEN = "#246b03"
YELLOW = "#fad817"
RED = "#ee1010"


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.depends("product_id", "product_uom_qty", "order_id.warehouse_id")
    def _compute_available_qty_for_popover(self):
        for line in self:
            line.available_qty_for_popover = line._get_available_qty_for_popover()

    def _get_available_qty_for_popover(self):
        self.ensure_one()
        if self.product_id:
            return self.product_id.get_warehouse_qty(self.order_id.warehouse_id)

    @api.depends("product_id", "product_uom_qty", "order_id.warehouse_id")
    def _compute_available_qty_popover_color(self):
        for line in self:
            if line.available_qty_for_popover >= line.product_uom_qty:
                line.available_qty_popover_color = GREEN
            elif line.available_qty_for_popover < line.product_uom_qty and \
                    line.product_id.qty_available >=  line.product_uom_qty:
                line.available_qty_popover_color = YELLOW
            else:
                line.available_qty_popover_color = RED
