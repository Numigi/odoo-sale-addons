# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        rec = super(AccountMove, self).create(vals)
        if (
            rec.team_id
            and rec.team_id.sales_journal_id
            and rec.team_id.sales_journal_id.currency_id == rec.currency_id
        ):
            rec.journal_id = rec.team_id.sales_journal_id.id
        return rec
