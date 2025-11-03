# -*- coding: utf-8 -*-

from odoo.tests.common import SavepointCase


class TestCRM(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCRM, cls).setUpClass()

        cls.res_users_model = cls.env["res.users"]
        cls.res_partner_model = cls.env["res.partner"]
        cls.crm_team_model = cls.env["crm.team"]
        cls.crm_lead_model = cls.env["crm.lead"]
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user1_id = cls.res_users_model.create(
            {
                "name": "User1",
                "login": "user1@gmail.com",
                "email": "user1@gmail.com",
            }
        )

        cls.user2_id = cls.res_users_model.create(
            {
                "name": "User2",
                "login": "user2@gmail.com",
                "email": "user2@gmail.com",
            }
        )
        cls.user3_id = cls.res_users_model.create(
            {
                "name": "User3",
                "login": "user3@gmail.com",
                "email": "user3@gmail.com",
            }
        )
        cls.partner_id = cls.res_partner_model.create(
            {
                "name": "Partner 1",
            }
        )

        cls.team_id = cls.crm_team_model.create(
            {
                "name": "Team A",
                "use_opportunities": True,
                "user_id": cls.user1_id.id,
                "member_ids": [(6, 0, [cls.user2_id.id])],
            }
        )
        cls.opp_id = cls.crm_lead_model.create(
            {
                "name": "opportunity partner 1",
                "type": "opportunity",
                "date_conversion": False,
                "partner_id": cls.partner_id.id,
                "team_id": cls.team_id.id,
                "user_id": cls.user2_id.id,
            }
        )
        cls.lead_1 = cls.env["crm.lead"].create(
            {
                "name": "Lead1",
                "type": "lead",
                "user_id": cls.user2_id.id,
                "team_id": cls.team_id.id,
                "partner_id": False,
                "contact_name": "John",
                "email_from": "john@test.example.com",
                "country_id": cls.env.ref("base.us").id,
            }
        )
        convert = (
            cls.env["crm.lead2opportunity.partner"]
            .with_context(
                {
                    "active_model": "crm.lead",
                    "active_id": cls.lead_1.id,
                    "active_ids": cls.lead_1.ids,
                }
            )
            .create({})
        )
        convert.action_apply()
