# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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

        cls.interval_rate = 0.05

    @data(
        (0, 0, 100),
        (0, 0.5, 100),  # 50% of 100k == 50k < 60k
        (0.3, 0.7, 75),  # (60k - 30k) / (70k - 30k)
        (0.5, 1, 20),  # (60k - 50k) / (100k - 50k)
        (1, 1, 0),
    )
    @unpack
    def test_interval_rate_completion(self, slice_from, slice_to, completion):
        rate = self._create_target_rate(self.target, slice_from, slice_to)
        self.category.rate_type = "interval"
        self.target.compute()
        assert rate.completion_rate == completion

    @data(
        (0, 0, 0),
        (0, 0.5, 2500),  # 50% of 50k = 25k
        (0.3, 0.7, 1500),  # 50% of 30k = 15k
        (0.5, 1, 500),  # 50% of 10k = 5k
        (1, 1, 0),
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
            self._create_target_rate(self.target, 0.5, 0.4)

    def test_max_amount(self):
        rate = self._create_target_rate(self.target, 0, 0.5)
        self.category.rate_type = "interval"
        self.target.compute()

        assert rate.max_amount == 50000

    def test_copy_target(self):
        rate = self._create_target_rate(self.target, 0, 0.5, self.interval_rate)
        rate.completion_rate = 50
        rate.subtotal = 100

        new_target = self.target.copy()
        new_rate = new_target.rate_ids
        assert len(new_rate) == 1
        assert not new_rate.completion_rate
        assert not new_rate.subtotal


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
                            "slice_to": 0.5,
                            "commission_percentage": 0.02,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "slice_from": 0.5,
                            "slice_to": 1,
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
        assert rates[0].slice_to == 0.5
        assert rates[0].commission_percentage == 0.02

        assert rates[1].slice_from == 0.5
        assert rates[1].slice_to == 1
        assert rates[1].commission_percentage == 0.04

    def test_onchange_twice(self):
        target = self.env["commission.target"].new({"category_id": self.category.id})
        target.onchange_category_id()
        target.onchange_category_id()
        assert len(target.rate_ids) == 2

    def test_onchange_no_rate_on_category(self):
        self.category.rate_ids.unlink()
        target = self.env["commission.target"].new({"category_id": self.category.id})
        target.onchange_category_id()
        assert len(target.rate_ids) == 0
