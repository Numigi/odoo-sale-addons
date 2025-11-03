from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    # ================================================================
    # 1-
    # ================================================================
    emails = fields.Char(string="Emails des membres", compute="_compute_emails", store=True)

    @api.depends("member_ids.email")
    def _compute_emails(self):
        for team in self:
            emails = [member.email for member in team.member_ids if member.email]
            team.emails = ", ".join(emails)

    # ================================================================
    # 2-
    # ================================================================

    # ---- Pour le cas de changement à partir l'interface utilisateur
    @api.onchange("user_id")
    def _onchange_user_id_add_to_members(self):
        for team in self:
            if team.user_id and team.user_id not in team.member_ids:
                team.member_ids |= team.user_id

    # ---- Pour le cas de création d\'un nouveau enregistrement
    @api.model
    def create(self, vals):
        team = super().create(vals)
        if team.user_id and team.user_id not in team.member_ids:
            team.member_ids |= team.user_id
        return team

    # --- Pour le cas de changement en base de données
    def write(self, vals):
        res = super().write(vals)
        for team in self:
            if team.user_id and team.user_id not in team.member_ids:
                team.member_ids |= team.user_id
        return res
