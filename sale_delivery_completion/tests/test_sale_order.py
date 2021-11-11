# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env["product.product"].create(
            {"name": "My Product 1", "type": "product"}
        )

        cls.product_2 = cls.env["product.product"].create(
            {"name": "My Product 2", "type": "consu"}
        )

        cls.service = cls.env["product.product"].create(
            {"name": "Service", "type": "service"}
        )

        cls.customer = cls.env["res.partner"].create(
            {"name": "My Customer", "customer": True}
        )

        cls.unit = cls.env.ref("uom.product_uom_unit")

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "order_line": [
                    (0, 0, cls._get_so_line_vals(cls.product_1, cls.unit, 10)),
                    (0, 0, cls._get_so_line_vals(cls.product_2, cls.unit, 10)),
                    (0, 0, cls._get_so_line_vals(cls.service, cls.unit, 1)),
                ],
            }
        )

        cls.line_1 = cls.sale_order.order_line[0]
        cls.line_2 = cls.sale_order.order_line[1]

        cls.sale_order.qty_delivered_method = "manual"

    @classmethod
    def _get_so_line_vals(cls, product, unit, qty):
        return {
            "product_id": product.id,
            "name": product.name,
            "product_uom": unit.id,
            "product_uom_qty": qty,
        }

    def test_no_product_delivered(self):
        assert self.sale_order.completion_rate == "0%"

    def test_partially_delivered(self):
        self.line_1.qty_delivered = 5
        assert self.sale_order.completion_rate == "25%"

    def test_fully_delivered(self):
        self.line_1.qty_delivered = 10
        self.line_2.qty_delivered = 10
        assert self.sale_order.completion_rate == "100%"

    def test_if_no_stockable_product__then_fully_delivered(self):
        self.product_1.type = "service"
        self.product_2.type = "service"
        assert self.sale_order.completion_rate == "100%"
