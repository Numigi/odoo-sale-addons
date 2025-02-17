# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class AccountMoveJournal(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_id = cls.env.ref("base.main_company")
        cls.client_id = cls.env["res.partner"].create({"name": "My Client"})
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "My Sale Journal",
                "type": "sale",
                "code": "MSJ",
                "currency_id": cls.env.ref("base.USD").id,
                "company_id": cls.company_id.id,
            }
        )
        cls.team_id = cls.env.ref("sales_team.team_sales_department")

    def test__01_team_journal_exists(self):
        self.team_id.write(
            {
                "company_id": self.company_id.id,
                "journal_id": self.journal.id,
            }
        )
        move = (
            self.env["account.move"]
            .with_context(default_move_type="out_invoice")
            .create(
                {
                    "ref": "test_invoice_1",
                    "partner_id": self.client_id.id,
                    "currency_id": self.env.ref("base.USD").id,
                    "company_id": self.company_id.id,
                    "team_id": self.team_id.id,
                }
            )
        )

        self.assertEqual(move.journal_id.name, self.journal.name)

    def test__02_team_journal_not_exists(self):
        self.team_id.journal_id = False
        move = self.env["account.move"].create(
            {
                "currency_id": self.env.ref("base.USD").id,
                "move_type": "out_invoice",
            }
        )
        self.assertNotEqual(move.journal_id, self.journal)

    def test__03_team_journal_exists_but_different_currency(self):
        move = self.env["account.move"].create(
            {
                "currency_id": self.env.ref("base.EUR").id,
                "move_type": "out_invoice",
            }
        )
        self.assertNotEqual(move.journal_id.name, self.journal.name)

    def test__04_in_invoice_journal_not_changed_by_team(self):
        move = self.env["account.move"].create(
            {
                "currency_id": self.env.ref("base.USD").id,
                "move_type": "entry",
            }
        )
        self.assertNotEqual(move.journal_id.name, self.journal.name)
