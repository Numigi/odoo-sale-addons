# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_qty_delivered(self):
        lines_to_compute = self.filtered(
            lambda l: l.qty_delivered_method == "stock_move"
        )
        for line in lines_to_compute:
            line.qty_delivered = line._compute_qty_delivered_from_moves()

        super(SaleOrderLine, self - lines_to_compute)._compute_qty_delivered()

    def _compute_qty_delivered_from_moves(self):
        """Include the supplier location when computing the delivered qty.

        In vanilla Odoo, only moves related to a customer location
        are included as deliveries.

        This method was copied from the method `_compute_qty_delivered`
        of module sale_stock and adapted.
        """
        qty = 0.0

        moves_done = self.move_ids.filtered(
            lambda r: r.state == "done"
            and not r.scrapped
            and self.product_id == r.product_id
        )

        for move in moves_done:
            is_delivery = move.location_dest_id.usage in ("customer", "supplier")
            if is_delivery:
                if not move.origin_returned_move_id or (
                    move.origin_returned_move_id and move.to_refund
                ):
                    qty += move.product_uom._compute_quantity(
                        move.product_uom_qty, self.product_uom
                    )
            elif not is_delivery and move.to_refund:
                qty -= move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_uom
                )

        return qty
