from odoo.tests import common, tagged
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestOnchangeMethods(common.TransactionCase):

    def setUp(self):
        super(TestOnchangeMethods, self).setUp()

        self.user1 = self.env["res.users"].create(
            {
                "name": "User Test 1",
                "login": "user1@test.com",
                "email": "user1@test.com",
            }
        )

        self.user2 = self.env["res.users"].create(
            {
                "name": "User Test 2",
                "login": "user2@test.com",
                "email": "user2@test.com",
            }
        )

        self.user3 = self.env["res.users"].create(
            {
                "name": "User Test 3",
                "login": "user3@test.com",
                "email": "user3@test.com",
            }
        )

        self.test_model = self.env["crm.team"]

    def test_on_change_member_ids_empty(self):
        record = self.test_model.create(
            {"name": "Test Team Empty", "member_ids": [(5, 0, 0)], "emails": ""}
        )

        record.on_change_member_ids()

        self.assertEqual(
            record.emails, "", "Emails devrait être vide quand aucun membre"
        )

    def test_on_change_member_ids_single_member(self):
        record = self.test_model.create(
            {
                "name": "Test Team Single",
                "member_ids": [(6, 0, [self.user1.id])],
                "emails": "",
            }
        )
        record.on_change_member_ids()
        expected_email = "user1@test.com,"
        self.assertEqual(
            record.emails, expected_email, f"Emails devrait être '{expected_email}'"
        )

    def test_on_change_member_ids_multiple_members(self):
        record = self.test_model.create(
            {
                "name": "Test Team Multiple",
                "member_ids": [(6, 0, [self.user1.id, self.user2.id, self.user3.id])],
                "emails": "",
            }
        )
        record.on_change_member_ids()
        expected_emails = "user1@test.com,user2@test.com,user3@test.com,"
        self.assertEqual(
            record.emails, expected_emails, f"Emails devrait être '{expected_emails}'"
        )

    def test_on_change_member_ids_preserves_existing(self):
        record = self.test_model.create(
            {
                "name": "Test Team Preserve",
                "member_ids": [(6, 0, [self.user1.id])],
                "emails": "existing@email.com,",
            }
        )
        record.on_change_member_ids()

        expected_emails = "user1@test.com,"
        self.assertEqual(
            record.emails,
            expected_emails,
            "Les emails existants devraient être remplacés",
        )

    def test_on_change_member_ids_user_without_login(self):
        user_no_login = self.env["res.users"].create(
            {
                "name": "User No Login",
                "login": False,
                "email": "nologin@test.com",
            }
        )
        record = self.test_model.create(
            {
                "name": "Test Team No Login",
                "member_ids": [(6, 0, [user_no_login.id, self.user1.id])],
                "emails": "",
            }
        )
        record.on_change_member_ids()
        expected_emails = "user1@test.com,"
        self.assertEqual(
            record.emails,
            expected_emails,
            "Seuls les utilisateurs avec login devraient être ajoutés aux emails",
        )

    def test_on_change_user_id_new_user(self):
        record = self.test_model.create(
            {
                "name": "Test Team New User",
                "member_ids": [(6, 0, [self.user1.id])],
                "user_id": self.user2.id,
                "emails": "",
            }
        )
        record.on_change_user_id()
        self.assertIn(
            self.user2,
            record.member_ids,
            "Le nouvel user_id devrait être ajouté aux member_ids",
        )
        self.assertIn(
            self.user1,
            record.member_ids,
            "Les membres existants devraient être conservés",
        )

    def test_on_change_user_id_existing_user(self):
        record = self.test_model.create(
            {
                "name": "Test Team Existing User",
                "member_ids": [(6, 0, [self.user1.id, self.user2.id])],
                "user_id": self.user1.id,  # user1 est déjà dans member_ids
                "emails": "",
            }
        )

        member_ids_before = record.member_ids.ids.copy()

        record.on_change_user_id()

        self.assertEqual(
            set(record.member_ids.ids),
            set(member_ids_before),
            "La liste des membres ne devrait pas changer si user_id est déjà présent",
        )

    def test_on_change_user_id_no_user_id(self):
        record = self.test_model.create(
            {
                "name": "Test Team No User",
                "member_ids": [(6, 0, [self.user1.id])],
                "user_id": False,
                "emails": "",
            }
        )

        member_ids_before = record.member_ids.ids.copy()

        record.on_change_user_id()

        self.assertEqual(
            record.member_ids.ids,
            member_ids_before,
            "La liste des membres ne devrait pas changer si user_id est vide",
        )

    def test_on_change_user_id_empty_members(self):
        record = self.test_model.create(
            {
                "name": "Test Team Empty Members",
                "member_ids": [(5, 0, 0)],  # Liste vide
                "user_id": self.user1.id,
                "emails": "",
            }
        )

        record.on_change_user_id()

        self.assertIn(
            self.user1,
            record.member_ids,
            "user_id devrait être ajouté aux member_ids quand la liste est vide",
        )
        self.assertEqual(len(record.member_ids), 1, "Devrait avoir exactement 1 membre")

    def test_combined_behavior(self):
        record = self.test_model.create(
            {
                "name": "Test Team Combined",
                "member_ids": [(6, 0, [self.user1.id])],
                "user_id": self.user2.id,
                "emails": "",
            }
        )

        record.on_change_user_id()

        self.assertIn(self.user2, record.member_ids)

        record.on_change_member_ids()

        expected_emails = "user1@test.com,user2@test.com,"
        self.assertEqual(
            record.emails,
            expected_emails,
            f"Emails devrait contenir les deux utilisateurs: '{expected_emails}'",
        )

    def test_on_change_member_ids_ordering(self):
        record = self.test_model.create(
            {
                "name": "Test Team Ordering",
                "member_ids": [(6, 0, [self.user3.id, self.user1.id, self.user2.id])],
                "emails": "",
            }
        )
        record.on_change_member_ids()
        expected_emails = "user3@test.com,user1@test.com,user2@test.com,"
        self.assertEqual(
            record.emails,
            expected_emails,
            "L'ordre des emails devrait correspondre à l'ordre des member_ids",
        )
