# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestDeliveryCarrier(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.carrier_a = cls.env.ref("delivery.free_delivery_carrier")
        cls.carrier_b = cls.carrier_a.copy()

    def test_search_without_filter(self):
        carrier = self.env["delivery.carrier"].search([("id", "=", self.carrier_a.id)])
        assert carrier == self.carrier_a

    def test_search_with_filter(self):
        carrier = (
            self.env["delivery.carrier"]
            .with_context(filter_delivery_carrier_ids=self.carrier_b.ids)
            .search([])
        )
        assert carrier == self.carrier_b
