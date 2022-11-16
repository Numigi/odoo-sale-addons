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
            res = self.product_id.with_context(
                from_sale_order=True, is_rental_sale=self.order_id.is_rental,warehouse=self.order_id.warehouse_id.id
            )._compute_quantities_dict(
                self._context.get("lot_id"),
                self._context.get("owner_id"),
                self._context.get("package_id"),
                self._context.get("from_date"),
                self._context.get("to_date"),
            )
            return res.get(self.product_id.id).get("qty_available")
        return self.product_id.with_context(company_owned=True).qty_available



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
