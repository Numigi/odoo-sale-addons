# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class CrmTeam(models.Model):
    _inherit = "crm.team"

    team_emails = fields.Char(
        translate=True,
        compute="_compute_mails",
        track_visibility="onchange"
        )

    user_id = fields.Many2one('res.users', string='Team Leader', check_company=True)


    @api.depends("member_ids")
    def _compute_mails(self):
        for rec in self:
            if rec.member_ids:
                mail = [membre.partner_id.email for membre in rec.member_ids]
                rec.team_emails = ';'.join(mail)
            else:
                rec.team_emails = ' '


    def write(self, values):
        res = super(CrmTeam, self).write(values)
        if values.get('user_id'):
            self.user_id.write({"sale_team_id": self.id})
        return res

