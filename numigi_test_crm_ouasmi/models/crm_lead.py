from odoo import models, fields, api
from datetime import datetime, timedelta



class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model
    def notify_stale_opportunities(self):
        limit_date = datetime.now() - timedelta(days=10)
        # stale_opps = self.search([
        #    ('type', '=', 'opportunity'),
        #    ('create_date', '<=', limit_date),
        #    ('active', '=', True),
        #    ('stage_id.sequence', '=', 1),
        # ])
        stale_opps = self.search(
            [
                ("type", "=", "opportunity"),
                ("active", "=", True),
                ("stage_id.sequence", "=", 1),
                "|",
                ("date_last_stage_update", "<=", limit_date),
                ("create_date", "<=", limit_date),
            ]
        )

        if not stale_opps:
            return

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        for opp in stale_opps:
            team = opp.team_id
            if team and team.member_ids:
                subject = "Opportunité sans mise à jour depuis 10 jours"
                link = f"{base_url}/web#id={opp.id}&model=crm.lead&view_type=form"
                body = (
                    f"Bonjour,<br/>"
                    f"Merci de donner une suite à cette opportunité "
                    f"<a href='{link}'>{opp.name}</a>.<br/><br/>"
                    f"Cordialement."
                )

                for user in team.member_ids:
                    if user.partner_id:
                        channel = self.env["mail.channel"].search(
                            [
                                ("channel_partner_ids", "in", [self.env.user.partner_id.id]),
                                ("channel_partner_ids", "in", [user.partner_id.id]),
                                ("channel_type", "=", "chat"),
                            ],
                            limit=1,
                        )

                        if not channel:
                            channel = self.env["mail.channel"].create(
                                {
                                    "channel_partner_ids": [
                                        (4, self.env.user.partner_id.id),
                                        (4, user.partner_id.id),
                                    ],
                                    "channel_type": "chat",
                                    "name": f"Opportunité - {opp.name}",
                                }
                            )

                        channel.message_post(
                            subject=subject,
                            body=body,
                            message_type="comment",
                            subtype_id=self.env.ref("mail.mt_comment").id,
                            partner_ids=[user.partner_id.id],
                        )

                opp.message_post(
                    body=(
                        "Une notification a été envoyée à tous les membres de l’équipe assignée à "
                        "l’opportunité."
                    ),
                    message_type="notification",
                    subtype_id=self.env.ref("mail.mt_note").id,
                )

        return True