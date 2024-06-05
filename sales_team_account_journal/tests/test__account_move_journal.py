# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class AccountMoveJournal(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "My Sale Journal",
                "type": "sale",
                "code": "MSJ",
                "currency_id": cls.env.ref("base.USD").id,
            }
        )
        cls.team_id = cls.env["crm.team"].create(
            {
                "name": "Super Sales Team",
                "journal_id": cls.journal.id,
            }
        )

    def test__01_team_journal_exists(self):
        move = self.env["account.move"].create(
            {
                "team_id": self.team_id.id,
                "currency_id": self.env.ref("base.USD").id,
            }
        )
        self.assertEqual(move.journal_id.name, self.journal.name)

    def test__02_team_journal_not_exists(self):
        self.team_id.journal_id = False
        move = self.env["account.move"].create(
            {
                "currency_id": self.env.ref("base.USD").id,
            }
        )
        self.assertNotEqual(move.journal_id, self.journal)

    def test__03_team_journal_exists_but_different_currency(self):
        self.journal.currency_id = self.env.ref("base.EUR").id
        move = self.env["account.move"].create(
            {
                "team_id": self.team_id.id,
                "currency_id": self.env.ref("base.USD").id,
            }
        )
        self.assertNotEqual(move.journal_id.name, self.journal.name)
