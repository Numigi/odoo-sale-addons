# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.http import request
from odoo.tests.common import SavepointCase
from odoo.addons.test_http_request.common import mock_odoo_request


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "My Product 1", "type": "product"}
        )

        cls.partner = cls.env.ref("base.res_partner_1")
        cls.user = cls.env.ref("base.user_demo")

        cls.unit = cls.env.ref("uom.product_uom_unit")

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "order_line": [
                    (0, 0, cls._get_so_line_vals(cls.product, cls.unit, 10)),
                ],
            }
        )

        cls.line_1 = cls.sale_order.order_line[0]

    @classmethod
    def _get_so_line_vals(cls, product, unit, qty):
        return {
            "product_id": product.id,
            "name": product.name,
            "product_uom": unit.id,
            "product_uom_qty": qty,
        }

    def test_update_cart(self):
        self._update_cart()
        assert not self.line_1.displayed_delay

    def test_update_cart__with_delay(self):
        self.product.inventory_availability = "threshold_warning"
        self.product.available_threshold = 9
        self.product.replenishment_delay = 2
        self._update_cart()
        assert self.line_1.displayed_delay == "2 days"

    def _update_cart(self):
        with mock_odoo_request(self.env(user=self.user)):
            request.session.update({
                'partner_id': self.partner.id,
                'sale_order_id': self.sale_order.id,
            })
            self.sale_order._cart_update(
                self.product.id, self.line_1.id, add_qty=0, set_qty=0
            )
