from odoo.tests import common


class TestCrmTeam(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.res_users = self.env["res.users"]
        self.team_model = self.env["your.module.team.model"]

        self.user_1 = self.res_users.create(
            {
                "name": "User One",
                "login": "user1@example.com",
                "email": "user1@example.com",
            }
        )
        self.user_2 = self.res_users.create(
            {
                "name": "User Two",
                "login": "user2@example.com",
                "email": "user2@example.com",
            }
        )

    def test_compute_all_team_members_emails(self):
        team = self.team_model.create(
            {
                "name": "Test Team",
                "member_ids": [(6, 0, [self.user_1.id, self.user_2.id])],
            }
        )

        self.assertIn(self.user_1.email, team.team_emails)
        self.assertIn(self.user_2.email, team.team_emails)
        self.assertEqual(team.team_emails, "user1@example.com, user2@example.com")

    def test_create_adds_user_to_members(self):
        team = self.team_model.create(
            {
                "name": "Auto Add User Team",
                "user_id": self.user_1.id,
            }
        )

        self.assertIn(self.user_1, team.member_ids)
        self.assertIn(self.user_1.email, team.team_emails)

    def test_onchange_user_adds_to_members(self):
        team = self.team_model.new({"name": "Onchange Team"})
        team.user_id = self.user_1
        team._onchange_user()
        self.assertIn(self.user_1, team.member_ids)
