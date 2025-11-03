from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    emails = fields.Char(
        "Emails",
    )

    @api.onchange("member_ids")
    def on_change_member_ids(self):
        self.emails = ""
        for member in self.member_ids:
            if member.login:
                self.emails += member.login + ","

    @api.onchange("user_id")
    def on_change_user_id(self):
        if self.user_id not in self.member_ids:
            self.member_ids += self.user_id
