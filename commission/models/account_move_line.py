# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    commission_target_ids = fields.Many2many(
        "commission.target",
        "commission_target_move_line_rel",
        "move_line_id",
        "target_id",
    )

    commission_target_count = fields.Integer(
        compute="_compute_commission_target_count",
        store=True,
    )

    @api.depends("commission_target_ids.state")
    def _compute_commission_target_count(self):
        for line in self:
            targets = line.commission_target_ids.filtered(
                lambda t: t.state not in ("draft", "cancelled")
            )
            line.commission_target_count = len(targets)
