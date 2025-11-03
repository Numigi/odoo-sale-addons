from odoo import models, fields, api, _


class CrmTeam(models.Model):
    _inherit = "crm.team"

    member_emails = fields.Text(
        string="Member Emails",
        compute="_compute_member_emails",
        store=False,
        help="List of team members' emails, separated by commas.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Crée les équipes et ajoute les leaders comme membres."""
        teams = super().create(vals_list)
        teams._add_leaders_to_members()
        return teams

    def write(self, vals):
        """Met à jour l'équipe et ajoute le nouveau leader aux membres si modifié."""
        result = super().write(vals)

        if 'user_id' in vals:
            self._add_leaders_to_members()

        return result

    @api.depends("member_ids", "member_ids.email")
    def _compute_member_emails(self):
        """Calcule la liste des emails des membres de l'équipe."""
        for team in self:
            team.member_emails = self._get_member_emails(team)

    def _add_leaders_to_members(self):
        """Add team leaders to members if not already present."""
        teams_to_update = self._get_teams_needing_leader_addition()
        for team in teams_to_update:
            team.sudo().write({"member_ids": [(4, team.user_id.id)]})

    def _get_teams_needing_leader_addition(self):
        """Return teams where leader is not in members."""
        return self.filtered(
            lambda t: t.user_id and t.user_id not in t.member_ids
        )

    def _get_member_emails(self, team):
        """Retourne les emails des membres séparés par des virgules."""
        emails = [
            m.email.strip()
            for m in team.member_ids
            if isinstance(m.email, str) and m.email
        ]
        return ", ".join(emails)