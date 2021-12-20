# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommissionCase
from ddt import ddt, data, unpack


@ddt
class TestCommissionFixed(CommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls._create_invoice(amount=5000)

        cls.target = cls._create_target(target_amount=100000)

    @data(
        (0, 0),
        (0.05, 250),  # 50% of 5k = 2.5k
        (1, 5000),  # 100% of 5k = 5k
    )
    @unpack
    def test_fixed_rate(self, rate, total):
        self.target.fixed_rate = rate
        self.category.rate_type = "fixed"
        self.target.compute()
        assert self.target.total_amount == total
