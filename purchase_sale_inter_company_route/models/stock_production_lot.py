# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    def _compute_sale_order_ids(self):
        """Restrain the field sale_order_ids to the current company.

        Otherwise, when accessing the form view of a serial number,
        an error is raised if a SO from another company is linked.
        """
        for lot in self:
            stock_moves = lot._get_related_stock_moves()

            orders = self.env["sale.order"].search(
                [
                    ("order_line.move_ids", "in", stock_moves.ids),
                    ("company_id", "child_of", self.env.user.company_id.id),
                ]
            )

            lot.sale_order_ids = orders
            lot.sale_order_count = len(orders)

    def _compute_purchase_order_ids(self):
        """Restrain the field purchase_order_ids to the current company.

        Idem as _compute_sale_order_ids, but for purchase orders.
        """
        for lot in self:
            stock_moves = lot._get_related_stock_moves()

            orders = self.env["purchase.order"].search(
                [
                    ("order_line.move_ids", "in", stock_moves.ids),
                    ("company_id", "child_of", self.env.user.company_id.id),
                ]
            )

            lot.purchase_order_ids = orders
            lot.purchase_order_count = len(orders)

    def _get_related_stock_moves(self):
        return self.env["stock.move"].search(
            [("move_line_ids.lot_id", "=", self.id), ("state", "=", "done")]
        )
