# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from datetime import timedelta


class SaleCommitmentDateUpdate(models.TransientModel):
    _name = "sale.commitment.date.update"
    _description = "Sale Commitment Date Update"

    order_id = fields.Many2one("sale.order")
    date = fields.Datetime()

    def confirm(self):
        done_moves = []
        for line in self.order_id.order_line:
            self._process_order_line(line, done_moves)
        self.order_id.commitment_date = self.date

    def _process_order_line(self, line, done_moves):
        delta = self._get_delta(line)
        moves = self._iter_all_stock_moves(line)
        moves_to_update = (m for m in moves if m not in done_moves)

        for move in moves_to_update:
            move.write({"date_expected": move.date_expected + delta})
            done_moves.append(move)

    def _iter_all_stock_moves(self, line):
        for step in self._iter_stock_move_steps(line):
            for move in step:
                yield move

    def _iter_stock_move_steps(self, line):
        moves = line.move_ids

        limit = 10
        while moves and limit:
            yield moves
            moves = moves.mapped("move_orig_ids")
            limit -= 1

    def _get_delta(self, line):
        initial_date = (
            self.order_id.commitment_date
            or self.order_id.confirmation_date + timedelta(line.customer_lead)
        )
        return self.date - initial_date
