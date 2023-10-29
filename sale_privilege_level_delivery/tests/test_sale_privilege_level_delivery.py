# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.level_a = cls.env["sale.privilege.level"].create(
            {"name": "Level A"})
        cls.level_b = cls.env["sale.privilege.level"].create(
            {"name": "Level B"})

        cls.carrier_a = cls.env.ref("delivery.free_delivery_carrier")
        cls.carrier_b = cls.carrier_a.copy()

        cls.carrier_a.privilege_level_ids = cls.level_a
        cls.carrier_b.privilege_level_ids = cls.level_b

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

    def test_get_available_delivery_carriers(self):
        result = self.partner.get_available_delivery_carriers()
        assert self.carrier_a in result
        assert self.carrier_b not in result

    def test_unfiltered_payment_carrier(self):
        self.carrier_b.privilege_level_ids = False
        result = self.partner.get_available_delivery_carriers()
        assert self.carrier_b in result

    def test_contact_inherits_privilege_levels_of_commercial_partner(self):
        result = self.child_partner.get_available_delivery_carriers()
        assert self.carrier_a in result
        assert self.carrier_b not in result

    def test_search_without_filter(self):
        carrier = self.env["delivery.carrier"].search(
            [("id", "=", self.carrier_b.id)])
        assert carrier == self.carrier_b

    def test_search_with_filter(self):
        available_carriers = (
            self.env["delivery.carrier"]
            .with_context(sale_privilege_level_partner_id=self.partner.id)
            .search([])
        )
        assert self.carrier_a in available_carriers
        assert self.carrier_b not in available_carriers

    def test_sale_order_filter(self):
        delivery_wizard = self.env['choose.delivery.carrier'].new({
            'order_id': self.order.id,

        })
        assert self.carrier_a.id in (
                delivery_wizard.available_carrier_ids.ids or
                delivery_wizard.available_carrier_ids._origin.ids)
        assert self.carrier_b.id not in (
                delivery_wizard.available_carrier_ids.ids and
                delivery_wizard.available_carrier_ids._origin.ids)
