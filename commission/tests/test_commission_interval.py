# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCommissionCase
from ddt import ddt, data
from ddt import unpack


@ddt
class TestCommissionInterval(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.invoice = cls._create_invoice(amount=60000)

    @data(
        (0, 0, 0),
        (0, 50, 1),  # 50% of 100k == 50k < 60k
        (50, 100, 0.2),  # (60k - 50k) / (100k - 50k)
        (100, 100, 0)
    )
    @unpack
    def test_interval_rate_completion(self, slice_from, slice_to, result):
        self.target.commissions_total = 
        rate = self._create_rate(slice_from, slice_to, 0)
        self.category.rate_type = "interval"
        self.target.compute()
        assert rate.completion == result

    """@data((0, 0, 0), (0, 50, 25000), (50, 100, 5000), (100, 100, 0))
    @unpack
    def test_interval_rate_subtotal(self, slice_from, slice_to, subtotal):
        rate = self._create_rate(slice_from, slice_to, 50)
        self.category.rate_type = "interval"
        self.target.compute()
        assert rate.subtotal == subtotal"""
