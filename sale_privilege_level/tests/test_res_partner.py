# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.level_a = cls.env["sale.privilege.level"].create(
            {"name": "Level A"})
        cls.level_b = cls.env["sale.privilege.level"].create(
            {"name": "Level B"})

    def test_partner_default_privilege_level(self):
        self.env.user.company_id.default_privilege_level_id = self.level_a
        partner = self.env["res.partner"].create({"name": "Partner A"})
        assert partner.get_privilege_level() == self.level_a

    def test_partner_onchange_parent_to_privilege_level(self):
        self.env.user.company_id.default_privilege_level_id = self.level_a
        partner = self.env["res.partner"].create({"name": "Partner A"})
        assert partner.privilege_level_id == self.level_a
        company = self.env["res.partner"].create(
            {
                "name": "Company A",
                "company_type": "company",
                "privilege_level_id": self.level_b.id,
            }
        )
        partner.parent_id = company.id
        partner._onchange_parent_to_privilege_level()
        assert partner.privilege_level_id == self.level_b
        # If changed by wizard or/and updated by write()
        company_b = company.copy()
        company_b.privilege_level_id = self.level_a.id
        partner.parent_id = company_b.id
        assert partner.privilege_level_id == self.level_a

    def test_user_default_privilege_level(self):
        self.env.user.company_id.default_privilege_level_id = self.level_a
        user = self.env["res.users"].create(
            {"name": "User A", "email": "a@example.com", "login": "a@example.com"}
        )
        assert user.partner_id.get_privilege_level() == self.level_a

    def test_user_default_privilege_level__on_copy(self):
        """Check that on user copy, the default privilege level is used.

        When a user is created on signup, the value is copied from the
        template partner.

        However, we want to override this value with the value defined
        in config settings.
        """
        user = self.env["res.users"].create(
            {"name": "User A", "email": "a@example.com", "login": "a@example.com"}
        )
        self.env.user.company_id.default_privilege_level_id = self.level_a
        user_2 = user.copy()
        assert user_2.partner_id.get_privilege_level() == self.level_a

    def test_contact_partner_uses_parent_privilege_level(self):
        self.env.user.company_id.default_privilege_level_id = self.level_a
        partner = self.env["res.partner"].create({"name": "Partner A"})
        contact = self.env["res.partner"].create(
            {"name": "Partner A", "type": "contact", "parent_id": partner.id}
        )
        assert contact.privilege_level_invisible
        assert not partner.privilege_level_invisible
        assert contact.get_privilege_level() == self.level_a
