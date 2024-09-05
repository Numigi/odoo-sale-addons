# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_team_journal(self, team_id, company_id, currency_id):
        return (
            True
            if team_id.journal_id
            and team_id.journal_id.company_id.id == company_id
            and team_id.journal_id.currency_id.id == currency_id
            else False
        )

    def _check_sale_move_type(self):
        move_type = self._context.get('default_move_type', 'entry')
        return True if move_type in self.get_sale_types(include_receipts=False) else False

    @api.onchange("team_id")
    def onchange_team_id(self):
        if self.team_id:
            if self._check_sale_move_type() and self._check_team_journal(
                self.team_id, self.company_id.id, self.currency_id.id
            ):
                self.journal_id = self.team_id.journal_id

    @api.model
    def create(self, vals):
        if vals.get("team_id", False):
            team_id = self.env["crm.team"].browse(vals["team_id"])
            company_id = vals.get("company_id", self.env.company.id)
            currency_id = vals.get("currency_id", False)
            if self._check_sale_move_type() and self._check_team_journal(
                team_id, company_id, currency_id
            ):
                vals["journal_id"] = team_id.journal_id.id
        return super(AccountMove, self).create(vals)
