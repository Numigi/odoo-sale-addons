# -*- coding: utf-8 -*-
import datetime
import json
from datetime import date

from lxml import etree
from odoo import models, api, _, fields
from werkzeug.urls import url_encode


class CrmLead(models.Model):
    _inherit = "crm.lead"

    is_notification_created = fields.Boolean(
        "Is notification created?", default=False, copy=False
    )

    def _cron_send_notification_to_members(self):
        lead_obj = self.env["crm.lead"]
        stage_new_id = self.env.ref("crm.stage_lead1")
        ten_days_ago = date.today() - datetime.timedelta(days=10)
        domain = [
            ("stage_id", "=", stage_new_id.id),
            ("type", "=", "opportunity"),
            ("is_notification_created", "=", False),
            ("team_id", "!=", False),
            ("team_id.member_ids", "not in", []),
            "|",
            "&",
            ("create_date", "<", ten_days_ago),
            ("date_conversion", "=", False),
            ("date_conversion", "<", ten_days_ago),
        ]

        crm_lead_ids = lead_obj.search(domain)
        if not crm_lead_ids:
            return
        for cl in crm_lead_ids:
            partner_ids = cl.team_id.member_ids.mapped("partner_id.id")
            url = url_encode(
                {
                    "id": cl.id,
                    "action": "crm.crm_lead_action_pipeline",
                    "model": "crm.lead",
                    "view_type": "form",
                    "menu_id": self.env.ref("crm.crm_menu_root").id,
                }
            )
            action_url = "/web#{}".format(url)
            subject = cl.name
            body = _(
                """
            <p><i>Hello,</i></p><br/>
            <p><i>Please follow up on this opportunity <a class='o_document_link' href={}>{}</a>.</i></p><br/>
                     
            <p><i>Regards,</i></p>
            """
            ).format(action_url, subject)

            message_id = (
                cl.sudo()
                .with_context(no_document=True)
                .message_notify(
                    body=body,
                    subject=subject,
                    email_from=cl.company_id.email_formatted,
                    partner_ids=partner_ids,
                    email_layout_xmlid="mail.mail_notification_light",
                )
            )
            if message_id:
                cl.is_notification_created = True

        return True

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        condition = (
            view_type == "kanban"
            and self._context.get("default_type") == "opportunity"
            and not self.env.user.has_group("sales_team.group_sale_manager")
        )
        if condition:
            view_id = self.env.ref(
                "numigi_test_crm_hbentaleb.crm_case_kanban_view_leads_inherit2"
            ).id

        res = super(CrmLead, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        doc = etree.XML(res["arch"])
        if view_type == "tree" and not self.env.user.has_group(
            "sales_team.group_sale_manager"
        ):
            for node in doc.xpath("//field[@name='expected_revenue']"):
                modifiers = json.loads(node.get("modifiers"))
                modifiers["column_invisible"] = True
                node.set("modifiers", json.dumps(modifiers))
        res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
