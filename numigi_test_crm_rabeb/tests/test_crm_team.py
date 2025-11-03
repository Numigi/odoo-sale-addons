from odoo.tests.common import TransactionCase


class TestCrmTeam(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.user_1 = cls.env["res.users"].create({
            "name": "User 1",
            "login": "user1",
            "email": "user1@test.com",
        })
        cls.user_2 = cls.env["res.users"].create({
            "name": "User 2",
            "login": "user2",
            "email": "user2@test.com",
        })

    def test_member_emails__two_members(self):
        team = self.env["crm.team"].create({"name": "Team"})
        team.write({"member_ids": [(6, 0, [self.user_1.id, self.user_2.id])]})

        assert team.member_emails == "user1@test.com, user2@test.com"

    def test_member_emails__no_members(self):
        team = self.env["crm.team"].create({"name": "Team"})

        assert team.member_emails == ""

    def test_member_emails__member_without_email(self):
        user_no_email = self.env["res.users"].create({
            "name": "No Email",
            "login": "noemail"
        })
        team = self.env["crm.team"].create({"name": "Team"})
        team.write({"member_ids": [(6, 0, [self.user_1.id, user_no_email.id])]})

        assert team.member_emails == "user1@test.com"

    def test_create__leader_added_to_members(self):
        team = self.env["crm.team"].create({
            "name": "Team",
            "user_id": self.user_1.id
        })

        assert self.user_1 in team.member_ids

    def test_write__new_leader_added_to_members(self):
        team = self.env["crm.team"].create({"name": "Team"})
        team.write({"user_id": self.user_1.id})

        assert self.user_1 in team.member_ids

    def test_write__leader_already_member_not_duplicated(self):
        team = self.env["crm.team"].create({
            "name": "Team",
            "user_id": self.user_1.id,
            "member_ids": [(6, 0, [self.user_1.id])]
        })
        team.write({"user_id": self.user_1.id})

        member_count = len([m for m in team.member_ids if m.id == self.user_1.id])
        assert member_count == 1

    def test_write__other_fields_no_impact(self):
        team = self.env["crm.team"].create({
            "name": "Team",
            "user_id": self.user_1.id,
        })
        initial_members = team.member_ids
        team.write({"name": "New Name"})

        assert team.member_ids == initial_members