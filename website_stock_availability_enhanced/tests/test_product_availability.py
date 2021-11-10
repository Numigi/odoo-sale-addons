# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data
from odoo.tests.common import SavepointCase


@ddt
class TestProductAvailability(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.user.company_id
        cls.product = cls.env["product.product"].create(
            {
                "name": "My Product",
                "type": "product",
            }
        )
        cls.product = cls.product.with_context(force_company=cls.company.id)
        cls.product_tmpl = cls.product.product_tmpl_id

    @data(
        "always",
        "threshold",
        "threshold_warning",
    )
    def test_show_availability(self, inventory_availability):
        self.product_tmpl.inventory_availability = inventory_availability
        info = self._get_combination_info(1)
        assert info["show_availability"]

    @data(
        "never",
        "custom",
    )
    def test_not_show_availability(self, inventory_availability):
        self.product_tmpl.inventory_availability = inventory_availability
        info = self._get_combination_info(1)
        assert not info.get("show_availability")

    def test_show_available_qty(self):
        self.product_tmpl.inventory_availability = "always"
        info = self._get_combination_info(1)
        assert info["show_available_qty"]
        assert info["available_qty"] == 0

    @data(
        "threshold",
        "threshold_warning",
    )
    def test_not_show_available_qty(self, inventory_availability):
        self.product_tmpl.inventory_availability = inventory_availability
        info = self._get_combination_info(1)
        assert not info.get("show_available_qty")

    @data(
        "threshold",
        "threshold_warning",
    )
    def test_show_available_qty_warning(self, inventory_availability):
        self.product_tmpl.inventory_availability = inventory_availability
        self.product_tmpl.available_threshold = 1
        self.product.sale_availability = 1
        info = self._get_combination_info(1)
        assert info["show_available_qty_warning"]
        assert info["available_qty"] == 1

    @data(
        "threshold",
        "threshold_warning",
    )
    def test_not_show_available_qty_warning(self, inventory_availability):
        self.product_tmpl.inventory_availability = inventory_availability
        self.product_tmpl.available_threshold = 1
        self.product.sale_availability = 2
        info = self._get_combination_info(1)
        assert not info.get("show_available_qty_warning")

    def test_show_in_stock(self):
        self.product_tmpl.inventory_availability = "threshold"
        self.product_tmpl.available_threshold = 1
        self.product.sale_availability = 2
        info = self._get_combination_info(1)
        assert info["show_in_stock"]

    def test_not_show_in_stock(self):
        self.product_tmpl.inventory_availability = "threshold"
        self.product_tmpl.available_threshold = 1
        info = self._get_combination_info(1)
        assert not info.get("show_in_stock")

    def test_show_replenishment_delay(self):
        self.product_tmpl.inventory_availability = "threshold"
        self.product.replenishment_delay = 10
        self.product.replenishment_availability = 1
        info = self._get_combination_info(1)
        assert info["show_replenishment_delay"]
        assert "10" in info["replenishment_delay_message"]
        assert info["replenishment_delay"] == 10

    def test_not_show_replenishment_delay(self):
        self.product_tmpl.inventory_availability = "threshold"
        self.product.replenishment_availability = 1
        info = self._get_combination_info(2)
        assert not info.get("show_replenishment_delay")
        assert not info.get("replenishment_delay_message")

    def _get_combination_info(self, add_qty):
        return self.product_tmpl.with_context(
            website_sale_stock_get_quantity=True
        )._get_combination_info(add_qty=add_qty)
