# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import data, ddt
from odoo.tests.common import SavepointCase
from odoo.tools.float_utils import float_round


@ddt
class TestDynamicPrice(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'price_type': 'dynamic',
            'minimum_margin': 0,
            'margin': 0,
            'price_rounding': 0,
            'price_surcharge': 0,
        })

    @data(
        # cost, margin, expected_margin_amount
        (100, 0.30, 42.86),  # 100 / (1 - 0.30) - 100
        (0, 0.30, 0),  # 0 / (1 - 0.30) - 0
        (100, 0, 0),  # 100 / (1 - 0) - 100
        (100, 1, 0),  # division by zero case
    )
    def test_compute_margin_amount(self, data_):
        cost, margin, expected_margin_amount = data_
        self.product.standard_price = cost
        self.product.margin = margin
        self.product.refresh()
        assert float_round(self.product.margin_amount, 2) == expected_margin_amount

    @data(
        # cost, margin, rounding, surcharge, expected_price
        (100, 0.20, '1', 0, 125),
        (100, 0.20, '10', 0, 130),
        (100, 0.20, '50', 0, 150),
        (100, 0.19, '50', 0, 100),
        (100, 0.19, '50', -0.01, 99.99),
        (53.44, 0, '1', -0.03, 52.97),
        (53.50, 0, '1', -0.01, 53.99),
        (53.46, 0, '0.5', -0.01, 53.49),
        (53.24, 0, '0.5', 0, 53.00),
        (53.25, 0, '0.5', 0, 53.50),
        (53.74, 0, '0.5', 0, 53.50),
        (53.75, 0, '0.5', 0, 54),
        (53.46, 0, '0.01', 0, 53.46),
        (53.42, 0, '0.05', 0, 53.40),
        (53.43, 0, '0.05', 0, 53.45),
        (53.47, 0, '0.05', 0, 53.45),
        (53.48, 0, '0.05', 0, 53.50),
        (12345.67, 0, '500', -0.01, 12499.99),
    )
    def test_compute_sale_price_from_cost(self, data_):
        cost, margin, rounding, surcharge, expected_price = data_
        self.product.write({
            'standard_price': cost,
            'margin': margin,
            'price_rounding': rounding,
            'price_surcharge': surcharge,
        })
        self.product.compute_sale_price_from_cost()
        self.product.refresh()
        assert round(self.product.list_price, 10) == expected_price

    def test_if_not_dynamic_price__sale_price_not_computed(self):
        expected_price = 999
        self.product.price_type = 'fixed'
        self.product.list_price = expected_price
        self.product.compute_sale_price_from_cost()
        self.product.refresh()
        assert self.product.list_price == expected_price

    def test_if_dynamic_price__sale_price_computed(self):
        expected_price = 999
        self.product.write({
            'standard_price': expected_price,
            'margin': 0,
            'price_rounding': 1,
            'price_surcharge': 0,
        })
        self.product.compute_sale_price_from_cost()
        self.product.refresh()
        assert self.product.list_price == expected_price
