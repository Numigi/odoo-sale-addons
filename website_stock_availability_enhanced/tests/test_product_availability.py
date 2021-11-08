# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data
from odoo.tests.common import SavepointCase


@ddt
class TestProductAvailability(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "My Product",
                "type": "product",
            }
        )
        cls.product_tmpl = cls.product.product_tmpl_id

    @data(
        "always",
        "threshold",
        "threshold_warning",
    )
    def test_show_product_availability(self, inventory_availability):
        self.product_tmpl.inventory_availability = inventory_availability
        info = self._get_combination_info()
        assert info["show_product_availability"]

    @data(
        "never",
        "custom",
    )
    def test_not_show_product_availability(self, inventory_availability):
        self.product_tmpl.inventory_availability = inventory_availability
        info = self._get_combination_info()
        assert not info["show_product_availability"]

    def test_always_show_available_qty(self):
        self.product_tmpl.inventory_availability = "always"
        info = self._get_combination_info()
        assert info["always_show_available_qty"]

    @data(
        "threshold",
        "threshold_warning",
    )
    def test_not_always_show_available_qty(self, inventory_availability):
        self.product_tmpl.inventory_availability = inventory_availability
        info = self._get_combination_info()
        assert not info["always_show_available_qty"]

    def test_enough_in_stock(self):
        self.product_tmpl.inventory_availability = "threshold"
        self._add_quant(1)
        info = self._get_combination_info()
        assert info["enough_in_stock"]

    def test_not_enough_in_stock(self):
        self.product_tmpl.inventory_availability = "threshold"
        info = self._get_combination_info()
        assert not info["enough_in_stock"]

    def _get_combination_info(self):
        return self.product_tmpl.with_context(
            website_sale_stock_get_quantity=True
        )._get_combination_info()

    def _add_quant(self, quantity):
        location = self.env.ref("stock.warehouse0").lot_stock_id
        self.env["stock.quant"].create(
            {
                "quantity": quantity,
                "location_id": location.id,
                "product_id": self.product.id,
            }
        )
