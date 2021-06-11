# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCommissionCase
from ddt import ddt, data
from ddt import unpack


@ddt
class TestCommissionFixed(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls._create_invoice(amount=5000)

    @data(
        (0, 0),
        (50, 2500),  # 50% of 5k = 2.5k
        (100, 5000),  # 100% of 5k = 5k
    )
    @unpack
    def test_fixed_rate(self, rate, total):
        self.target.fixed_rate = rate
        self.category.rate_type = "fixed"
        self.target.compute()
        assert self.target.commissions_total == total
