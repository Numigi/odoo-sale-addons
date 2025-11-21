from odoo import fields, models, api
from dateutil.relativedelta import relativedelta


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model
    def _ten_days_ago(self):
        datetime_ago = fields.Datetime.now() - relativedelta(Days=10)
        check_dratf_opportinuties = self.search(
            [
                ("create_date", "<=", datetime_ago),
                ("stage_id", "=", self.env.ref("crm.stage_lead1").id),
            ]
        )
        for opportinuty in check_dratf_opportinuties:
            if opportinuty.team_id and opportinuty.team_id.member_ids:
                opportinuty._get_notify_team_members()

    def _get_notify_team_members(self):
        body_html = self.env.ref(
            "numigi_test_crm_yamna_azzirari.email_template_team_members_reminder"
        )._render_field("body_html", self.ids, compute_lang=True)[self.id]
        for member in self.team_id.member_ids:
            member.partner_id.message_post(
                body=body_html,
                partner_ids=[member.partner_id.id],
            )

