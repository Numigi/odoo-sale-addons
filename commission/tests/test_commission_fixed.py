# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCommissionCase


class TestCommissionFixed(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls._create_invoice(amount=5000)

    def test_fixed_rate(self):
        self.target.fixed_rate = 10
        self.category.rate_type = "fixed"
        self.target.compute()
        assert self.target.commissions_total == 500
