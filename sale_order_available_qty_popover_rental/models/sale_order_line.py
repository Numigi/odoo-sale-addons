# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_available_qty_for_popover(self):
        self.ensure_one()
        if self.product_id:
            res = self.product_id.with_context(
                from_sale_order=True, is_rental_sale=self.order_id.is_rental
            )._compute_quantities_dict(
                self._context.get("lot_id"),
                self._context.get("owner_id"),
                self._context.get("package_id"),
                self._context.get("from_date"),
                self._context.get("to_date"),
            )
            return res.get(self.product_id.id).get("qty_available")
        return self.product_id.with_context(company_owned=True).qty_available
