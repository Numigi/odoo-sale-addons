from odoo import fields, models, api


class Team(models.Model):
    _inherit = "crm.team"

    team_emails = fields.Char(
        string="Team Members Emails",
        compute="_compute_all_team_members_emails",
    )

    def _compute_all_team_members_emails(self):
        for team in self:
            all_emails = team.member_ids.mapped("email")
            team.team_emails = ", ".join(email for email in all_emails if email)

    @api.model
    def create(self, vals):
        team = super().create(vals)
        if team.user_id.id and team.user_id.id not in team.member_ids.ids:
            team.member_ids = [(4, team.user_id.id)]
        return team

    @api.onchange("user_id")
    def _onchange_user(self):
        for team in self:
            if team.user_id.id and team.user_id.id not in team.member_ids.ids:
                team.member_ids = [(4, team.user_id.id)]
