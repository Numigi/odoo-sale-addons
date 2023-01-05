# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import data, ddt, unpack
from odoo.tests.common import SavepointCase


@ddt
class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Product A"})

        cls.customer = cls.env["res.partner"].create(
            {"name": "My Customer"}
        )

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.line = cls._create_sale_order_line(cls.order)

    @classmethod
    def _create_sale_order_line(cls, order):
        return cls.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": cls.product.id,
                "name": cls.product.name,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 1,
            }
        )

    @data((70, 100, 0.3), (70, 0, 0))
    @unpack
    def test_line_margin(self, cost, sale_price, expected_margin):
        self.line.purchase_price = cost
        self.line.price_unit = sale_price
        assert self.line.margin_percent == expected_margin

    @data((70, 100, 0.3), (70, 0, 0))
    @unpack
    def test_order_margin(self, cost, sale_price, expected_margin):
        self.line.purchase_price = cost
        self.line.price_unit = sale_price
        assert self.order.margin_percent == expected_margin

    def test_order_margin_with_2_lines(self):
        self.line.purchase_price = 30
        self.line.price_unit = 140

        line_2 = self._create_sale_order_line(self.order)
        line_2.purchase_price = 20
        line_2.price_unit = 60

        assert self.order.margin_percent == 0.75  # (140 + 60) - (30 + 20) / (140 + 60)
