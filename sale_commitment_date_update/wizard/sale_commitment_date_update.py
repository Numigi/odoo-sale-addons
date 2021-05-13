# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _
from datetime import timedelta


class SaleCommitmentDateUpdate(models.TransientModel):
    _name = "sale.commitment.date.update"
    _description = "Sale Commitment Date Update"

    order_id = fields.Many2one("sale.order")
    date = fields.Datetime(required=True)

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
        new_date = self._compute_stock_move_date(move)
        move.with_context(do_not_propagate=True).write({"date_expected": new_date})

    def _compute_stock_move_date(self, move):
        stock_move_delay = self._get_stock_move_delay(move)
        security_lead_time = self.order_id.company_id.security_lead
        return self.date - timedelta(stock_move_delay) - timedelta(security_lead_time)

    def _get_stock_move_delay(self, move):
        limit = 10
        days = 0

        while move and limit:
            days += move.mapped("rule_id")[:1].delay or 0

            if move.mapped("sale_line_id"):
                return days

            move = move.move_dest_ids
            limit -= 1

        return days

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
