# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    destination_sale_line_id = fields.Many2one(
        "sale.order.line",
        "Destination Sale Order Line",
        compute="_compute_destination_sale_line_id",
    )

    def _compute_destination_sale_line_id(self):
        for move in self:
            move.destination_sale_line_id = move._find_destination_sale_line()

    def _find_destination_sale_line(self):
        moves = self
        limit = 10

        while moves and not moves.mapped("sale_line_id") and limit:
            moves = moves.mapped("move_dest_ids")
            limit -= 1

        return moves.mapped("sale_line_id")[:1]

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        result = super()._prepare_merge_moves_distinct_fields()
        result.append("destination_sale_line_id")
        return result
