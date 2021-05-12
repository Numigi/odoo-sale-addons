# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _
from datetime import timedelta


class SaleCommitmentDateUpdate(models.TransientModel):
    _name = "sale.commitment.date.update"
    _description = "Sale Commitment Date Update"

    order_id = fields.Many2one("sale.order")
    date = fields.Datetime()

    def confirm(self):
        self._propagate_date()
        self.order_id.commitment_date = self.date
        self.order_id.message_post(
            body=_("Commitment date changed to {}").format(
                fields.Datetime.to_string(self.date)
            )
        )

    def _propagate_date(self):
        for move in self._iter_stock_moves_to_update():
            self._process_stock_move(move)

    def _process_stock_move(self, move):
        delta = self._get_delta(move.product_id)
        move.with_context(do_not_propagate=True).write(
            {"date_expected": move.date_expected + delta}
        )

    def _iter_stock_moves_to_update(self):
        all_moves = self._get_all_stock_moves()
        return (m for m in all_moves if m.state not in ("done", "cancel"))

    def _get_all_stock_moves(self):
        result = self.env["stock.move"]

        for moves in self._iter_stock_move_steps():
            result |= moves

        return result

    def _iter_stock_move_steps(self):
        moves = self.order_id.mapped("order_line.move_ids")

        limit = 10
        while moves and limit:
            yield moves
            moves = moves.mapped("move_orig_ids")
            limit -= 1

    def _get_delta(self, product):
        initial_date = (
            self.order_id.commitment_date
            or self.order_id.confirmation_date
            + timedelta(product.product_tmpl_id.sale_delay)
        )
        return self.date - initial_date
