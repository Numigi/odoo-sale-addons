# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytest
from .common import TestCommissionCase
from ddt import ddt, data, unpack
from odoo.exceptions import ValidationError


@ddt
class TestCommissionInterval(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.target = cls._create_target(target_amount=100000)

        cls._create_invoice(amount=60000)

        cls.interval_rate = 5

    @data(
        (0, 0, 1),
        (0, 50, 1),  # 50% of 100k == 50k < 60k
        (30, 70, 0.75),  # (60k - 30k) / (70k - 30k)
        (50, 100, 0.2),  # (60k - 50k) / (100k - 50k)
        (100, 100, 0),
    )
    @unpack
    def test_interval_rate_completion(self, slice_from, slice_to, completion):
        rate = self._create_target_rate(self.target, slice_from, slice_to)
        self.category.rate_type = "interval"
        self.target.compute()
        assert rate.completion_rate == completion

    @data(
        (0, 0, 0),
        (0, 50, 2500),  # 50% of 50k = 25k
        (30, 70, 1500),  # 50% of 30k = 15k
        (50, 100, 500),  # 50% of 10k = 5k
        (100, 100, 0),
    )
    @unpack
    def test_interval_rate_subtotal(self, slice_from, slice_to, subtotal):
        rate = self._create_target_rate(
            self.target, slice_from, slice_to, self.interval_rate
        )
        self.category.rate_type = "interval"
        self.target.compute()
        assert rate.subtotal == subtotal

    def test_interval_date_invalid(self):
        with pytest.raises(ValidationError):
            self._create_target_rate(self.target, 50, 40)


class TestRatesPropagation(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category.write(
            {
                "rate_type": "interval",
                "rate_ids": [
                    (
                        0,
                        0,
                        {
                            "slice_from": 0,
                            "slice_to": 50,
                            "commission_percentage": 0.02,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "slice_from": 50,
                            "slice_to": 100,
                            "commission_percentage": 0.04,
                        },
                    ),
                ],
            }
        )

    def test_onchange(self):
        target = self.env["commission.target"].new({"category_id": self.category.id})
        target.onchange_category_id()

        rates = target.rate_ids
        assert len(rates) == 2
        assert rates[0].slice_from == 0
        assert rates[0].slice_to == 50
        assert rates[0].commission_percentage == 0.02

        assert rates[1].slice_from == 50
        assert rates[1].slice_to == 100
        assert rates[1].commission_percentage == 0.04
