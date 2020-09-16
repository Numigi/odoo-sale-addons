# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestPaymentAcquirer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.acquirer_a = cls.env.ref("payment.payment_acquirer_transfer")
        cls.acquirer_b = cls.env.ref("payment.payment_acquirer_sips")

    def test_search_without_filter(self):
        acquirer = self.env["payment.acquirer"].search(
            [("id", "=", self.acquirer_a.id)]
        )
        assert acquirer == self.acquirer_a

    def test_search_with_filter(self):
        acquirer = (
            self.env["payment.acquirer"]
            .with_context(filter_payment_acquirer_ids=self.acquirer_b.ids)
            .search([])
        )
        assert acquirer == self.acquirer_b
