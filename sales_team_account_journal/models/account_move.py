# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("team_id")
    def onchange_team_id(self):
        if (
            self.team_id
            and self.team_id.journal_id
            and (
                not self.team_id.journal_id.currency_id
                or self.team_id.journal_id.currency_id == self.currency_id
            )
            and self.team_id.journal_id.company_id == self.company_id
        ):
            self.journal_id = self.team_id.journal_id

    @api.model
    def create(self, vals):
        rec = super(AccountMove, self).create(vals)
        if (
            rec.team_id
            and rec.team_id.journal_id
            and (
                not rec.team_id.journal_id.currency_id
                or rec.team_id.journal_id.currency_id == rec.currency_id
            )
            and rec.team_id.journal_id.company_id == rec.company_id
        ):
            rec.journal_id = rec.team_id.journal_id.id
        return rec
