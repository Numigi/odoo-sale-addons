# -*- coding: utf-8 -*-


from odoo.addons.numigi_test_crm_hbentaleb.tests.common import TestCRM


class TestCRMTeam(TestCRM):
    def test_user_added_to_members_create(self):
        self.assertEqual(
            self.team_id.member_ids.mapped("id"), self.user1_id.ids + self.user2_id.ids
        )

    def test_user_added_to_members_write(self):
        self.team_id.write({"user_id": self.user3_id.id})
        self.assertEqual(
            self.team_id.member_ids.mapped("id"),
            self.user1_id.ids + self.user2_id.ids + self.user3_id.ids,
        )
