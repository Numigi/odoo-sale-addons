# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.level_a = cls.env["sale.privilege.level"].create({"name": "Level A"})
        cls.level_b = cls.env["sale.privilege.level"].create({"name": "Level B"})

        cls.acquirer_a = cls.env.ref("payment.payment_acquirer_transfer")
        cls.acquirer_b = cls.env.ref("payment.payment_acquirer_sips")

        cls.acquirer_a.privilege_level_ids = cls.level_a
        cls.acquirer_b.privilege_level_ids = cls.level_b

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner A",
                "is_company": True,
                "privilege_level_id": cls.level_a.id,
            }
        )

        cls.child_partner = cls.env["res.partner"].create(
            {"name": "Contact", "parent_id": cls.partner.id}
        )

    def test_get_available_payment_acquirers(self):
        result = self.partner.get_available_payment_acquirers()
        assert self.acquirer_a in result
        assert self.acquirer_b not in result

    def test_unfiltered_payment_acquirer(self):
        self.acquirer_b.privilege_level_ids = False
        result = self.partner.get_available_payment_acquirers()
        assert self.acquirer_b in result

    def test_contact_inherits_privilege_levels_of_commercial_partner(self):
        result = self.child_partner.get_available_payment_acquirers()
        assert self.acquirer_a in result
        assert self.acquirer_b not in result

    def test_search_without_filter(self):
        acquirer = self.env["payment.acquirer"].search(
            [("id", "=", self.acquirer_b.id)]
        )
        assert acquirer == self.acquirer_b

    def test_search_with_filter(self):
        available_acquirers = (
            self.env["payment.acquirer"]
            .with_context(sale_privilege_level_partner_id=self.partner.id)
            .search([])
        )
        assert self.acquirer_a in available_acquirers
        assert self.acquirer_b not in available_acquirers
