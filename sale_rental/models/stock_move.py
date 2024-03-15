# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class StockMove(models.Model):

    _inherit = "stock.move"

    is_rental = fields.Boolean(
        related="location_dest_id.is_rental_customer_location",
        store=True,
    )
    is_ongoing_rental = fields.Boolean(
        compute="_compute_is_ongoing_rental",
        store=True,
    )

    @api.depends("state", "move_dest_ids.state")
    def _compute_is_ongoing_rental(self):
        for move in self:
            move.is_ongoing_rental = move._get_is_ongoing_rental()

    def _get_is_ongoing_rental(self):
        if not self.is_rental:
            return False

        if self.state != "done":
            return False

        if self._is_completely_returned():
            return False

        return True

    def _is_completely_returned(self):
        returned_moves = self.move_dest_ids.filtered(lambda m: m.state == "done")
        returned_qty = sum(returned_moves.mapped("product_qty"))
        return not float_compare(returned_qty, self.product_qty, 2)

    def write(self, vals):
        """Prevent propagating the expected date from a rental move to the return move.

        The expected date of a rental return is not updated from the rental delivery.
        It is updated only when the return date is set on the sale order line.

        Otherwise, when the delivery is processed, the effective date of delivery
        is propagated as expected date on the return move.
        """
        if "date" in vals:
            rental_moves = self.filtered(lambda m: m.is_rental_move())
            rental_moves_without_propagation = rental_moves.with_context(
                do_not_propagate=True
            )
            other_moves = self - rental_moves
            super(StockMove, rental_moves_without_propagation).write(dict(vals))
            super(StockMove, other_moves).write(dict(vals))
        else:
            return super().write(vals)

    def _action_done(self, cancel_backorder=False):
        result = super()._action_done(cancel_backorder=cancel_backorder)

        important_rental_moves = self.sudo().filtered(
            lambda m: m.is_important_component_move() and m.is_rental_move()
        )
        for move in important_rental_moves:
            move._update_sale_rental_service_line_delivered_qty()
            move._update_sale_rental_service_line_date_from()

        important_return_moves = self.sudo().filtered(
            lambda m: m.is_important_component_move() and m.is_rental_return_move()
        )
        for move in important_return_moves:
            move._update_sale_rental_service_line_returned_qty()
            move._update_sale_rental_service_line_date_to()

        return result

    def _update_sale_rental_service_line_delivered_qty(self):
        kit_line = self._get_sale_kit_line()
        service_line = self._get_sale_rental_service_line()
        service_line.write({"kit_delivered_qty": kit_line.qty_delivered})

    def _update_sale_rental_service_line_returned_qty(self):
        kit_line = self._get_sale_kit_line()
        service_line = self._get_sale_rental_service_line()
        service_line.write({"kit_returned_qty": kit_line.rental_returned_qty})

    def _update_sale_rental_service_line_date_from(self):
        kit_line = self._get_sale_kit_line()
        service_line = self._get_sale_rental_service_line()

        if kit_line.qty_delivered >= 1 and kit_line.state == "sale":
            service_line.rental_date_from = datetime.now()
            service_line.onchange_rental_dates()

    def _update_sale_rental_service_line_date_to(self):
        kit_line = self._get_sale_kit_line()
        service_line = self._get_sale_rental_service_line()

        if kit_line.rental_returned_qty >= 1 and kit_line.state == "sale":
            service_line.rental_date_to = datetime.now()
            service_line.onchange_rental_dates()

    def _get_sale_rental_service_line(self):
        kit_line = self._get_sale_kit_line()
        return kit_line.mapped("kit_line_ids").filtered(lambda l: l.is_rental_service)

    def _get_sale_kit_line(self):
        sale_line = self.sale_line_id
        return sale_line if sale_line.is_kit else sale_line.kit_id

    def is_processed_move(self):
        return self.state in ("done", "cancel")

    def is_done_move(self):
        return self.state == "done"

    def is_important_component_move(self):
        sale_line = self.sale_line_id
        return sale_line.is_important_kit_component or sale_line.is_kit

    def is_rental_move(self):
        return self.location_dest_id.is_rental_customer_location

    def is_rental_return_move(self):
        return self.location_id.is_rental_customer_location

    def set_expected_date(self, date_):
        self.write({"date": date_})

    def with_all_origin_moves(self):
        origin_moves = self.mapped("move_orig_ids")
        if not origin_moves:
            return self
        return self | origin_moves.with_all_origin_moves()
