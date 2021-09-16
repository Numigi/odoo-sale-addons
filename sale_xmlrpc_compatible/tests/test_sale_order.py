# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "invoice_policy": "order",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Lucas",
            }
        )

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

        cls.line = cls.env["sale.order.line"].create(
            {
                "product_id": cls.product.id,
                "order_id": cls.order.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1,
                "name": "line",
                "price_unit": 100,
            }
        )

    def test_update_prices(self):
        res = self.order.update_prices()
        assert res is True
