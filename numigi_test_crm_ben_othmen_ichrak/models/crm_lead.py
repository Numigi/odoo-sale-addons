from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def cron_notification_ten_days(self):
        leads = self.search([("stage_id.name", "=", "Draft")])
        for lead in leads:
            if (fields.Date.today() - lead.create_date.date()).days > 10:
                activity_type_id = (
                    lead.env["mail.activity.type"]
                    .sudo()
                    .search([("name", "=", "To Do")], limit=1)
                    .id
                )
                for user in lead.team_id.member_ids:
                    summary = (
                        "Bonjour,\nMerci de donner une suite à cette opportunité"
                        + lead.name
                        + ".\n"
                        "Cordialement."
                    )
                    lead.env["mail.activity"].sudo().create(
                        {
                            "activity_type_id": activity_type_id,
                            "summary": summary,
                            "note": summary,
                            "user_id": user.id,
                            "res_id": lead.id,
                            "res_model_id": lead.env["ir.model"]
                            .sudo()
                            .search([("model", "=", "crm.lead")], limit=1)
                            .id,
                        }
                    )
