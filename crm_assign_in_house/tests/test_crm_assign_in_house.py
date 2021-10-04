# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestCRMLead(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.salesperson = cls.env["res.users"].create(
            {"name": "Salesperson", "login": "salesperson", "email": "test@example.com"}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "My Partner",
                "in_house": True,
                "user_id": cls.salesperson.id,
            }
        )
        cls.contact = cls.env["res.partner"].create(
            {
                "name": "My Contact",
                "parent_id": cls.partner.id,
            }
        )
        cls.lead = cls.env["crm.lead"].create(
            {
                "name": "My Lead",
                "partner_id": cls.contact.id,
                "user_id": False,
            }
        )

    def test_onchange_partner_in_house(self):
        self.lead._onchange_partner_in_house()
        assert self.lead.user_id == self.salesperson

    def test_onchange_partner_not_in_house(self):
        self.partner.in_house = False
        self.lead._onchange_partner_in_house()
        assert not self.lead.user_id
