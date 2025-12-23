# -*- coding: utf-8 -*-
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api


class CrmTeam(models.Model):
    _inherit = "crm.team"

    emails = fields.Char(string="Member emails", store=True, compute="_compute_emails")

    @api.depends("member_ids")
    def _compute_emails(self):
        for team in self:
            email_list = team.member_ids.mapped("email")
            team.emails = ", ".join(filter(None, email_list))

    @api.onchange("user_id")
    def _onchange_user_id_add_to_members(self):
        if self.user_id and self.user_id not in self.member_ids:
            self.member_ids = [(4, self.user_id.id)]

    @api.model
    def create(self, vals):
        team = super(CrmTeam, self).create(vals)
        if team.user_id and team.user_id not in team.member_ids:
            team.member_ids = [(4, team.user_id.id)]
        return team

    def write(self, vals):
        res = super(CrmTeam, self).write(vals)
        for team in self:
            if team.user_id and team.user_id not in team.member_ids:
                team.member_ids = [(4, team.user_id.id)]
        return res
