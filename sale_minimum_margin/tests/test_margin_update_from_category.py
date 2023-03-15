# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import data, ddt
from odoo.tests.common import SavepointCase


@ddt
class TestMinimumMarginUpdate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["product.category"].create(
            {
                "name": "Category A",
                "minimum_margin": 0.30,
            }
        )
        cls.margin_1 = 0.30
        cls.list_price_1 = 100
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "categ_id": cls.category.id,
                "price_type": "dynamic",
                "standard_price": 70,
                "margin": cls.margin_1,
                "list_price": cls.list_price_1,
            }
        )
        cls.margin_2 = 0.40
        cls.list_price_2 = 200
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "type": "product",
                "categ_id": cls.category.id,
                "price_type": "dynamic",
                "standard_price": 120,
                "margin": cls.margin_2,
                "list_price": cls.list_price_2,
            }
        )

    def test_if_minimum_margin_greater_than_margin__price_is_increased(self):
        self.category.minimum_margin = 0.50
        (self.product_1 | self.product_2).refresh()
        assert self.product_1.list_price > self.list_price_1
        assert self.product_2.list_price > self.list_price_2

    @data(0.39, 0.40)
    def test_if_minimum_margin_not_greater_than_margin__price_unchanged(self, margin):
        self.category.minimum_margin = margin
        (self.product_1 | self.product_2).refresh()
        assert self.product_1.list_price > self.list_price_1
        assert self.product_2.list_price == self.list_price_2

    def test_if_product_is_not_in_category__price_unchanged(self):
        self.product_1.categ_id = self.category.copy()
        self.category.minimum_margin = 0.50
        (self.product_1 | self.product_2).refresh()
        assert self.product_1.list_price == self.list_price_1
        assert self.product_2.list_price > self.list_price_2

    def test_if_product_has_fixed_price__price_unchanged(self):
        self.product_1.price_type = "fixed"
        self.category.minimum_margin = 0.50
        (self.product_1 | self.product_2).refresh()
        assert self.product_1.list_price == self.list_price_1
        assert self.product_2.list_price > self.list_price_2
