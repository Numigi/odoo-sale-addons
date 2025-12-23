# -*- coding: utf-8 -*-
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0).

from odoo.tests.common import TransactionCase


class TestCrmTeam(TransactionCase):
    def setUp(self):
        super(TestCrmTeam, self).setUp()
        self.user_demo = self.env.ref("base.user_demo")
        self.user_admin = self.env.ref("base.user_admin")

        self.sales_team = self.env["crm.team"].create(
            {"name": "test sales team", "use_opportunities": True}
        )

    def test_010_compute_emails(self):
        self.assertEqual(self.sales_team.emails, "")
        self.sales_team.member_ids = self.user_admin | self.user_demo
        self.assertEqual(
            self.sales_team.emails, f"{self.user_demo.email},{self.user_admin.email}"
        )

    def test_020_add_team_leader_to_members(self):
        self.sales_team.member_ids |= self.user_demo
        self.assertEqual(self.sales_team.member_ids.ids[0], self.user_demo.id)
        self.sales_team.user_id = self.user_admin
        self.assertEqual(
            self.sales_team.member_ids.ids, (self.user_demo + self.user_admin).ids
        )
