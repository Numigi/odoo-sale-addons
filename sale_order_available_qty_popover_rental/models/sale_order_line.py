# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_available_qty_for_popover(self):
        if self.order_id.is_rental is False:
            return self._get_available_qty_for_popover_sale()
        else:
            return self._get_available_qty_for_popover_rental()

    def _get_available_qty_for_popover_sale(self):
        stock_quant_domain = [
            ("product_id", "=", self.product_id.id),
            ("location_id", "in", self._get_location_for_sale()),
        ]
        stock_quants_ids = self.env["stock.quant"].search(stock_quant_domain)
        return sum(stock_quants_ids.mapped("quantity"))

    def _get_available_qty_for_popover_rental(self):
        stock_quant_domain = [
            ("product_id", "=", self.product_id.id),
            ("location_id", "in", self._get_location_for_rental()),
        ]
        stock_quants_ids = self.env["stock.quant"].search(stock_quant_domain)
        return sum(stock_quants_ids.mapped("quantity"))

    def _get_location_for_sale(self):
        location_domain = [
            ("usage", "=", "internal"),
            ("is_rental_customer_location", "=", False),
        ]
        return self.env["stock.location"].search(location_domain).ids

    def _get_location_for_rental(self):
        location_domain = [
            ("usage", "=", "internal"),
            ("is_rental_customer_location", "=", True),
        ]
        return self.env["stock.location"].search(location_domain).ids
