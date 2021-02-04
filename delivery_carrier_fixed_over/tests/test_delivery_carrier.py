# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestDeliveryCarrier(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Product A"})
        cls.delivery_product = cls.env["product.product"].create({"name": "Delivery"})

        cls.customer = cls.env["res.partner"].create(
            {"name": "My Customer", "customer": True}
        )

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

        cls.minimum_amount = 100
        cls.line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product.id,
                "name": cls.product.name,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 1,
                "price_unit": cls.minimum_amount,
            }
        )

        cls.standard_shipping_amount = 50
        cls.reduced_shipping_amount = 40

        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "My Carrier",
                "delivery_type": "fixed",
                "fixed_price": cls.standard_shipping_amount,
                "enable_fixed_over": True,
                "fixed_over": cls.minimum_amount,
                "fixed_over_amount": cls.reduced_shipping_amount,
                "product_id": cls.delivery_product.id,
            }
        )

    def test_checkbox_not_checked(self):
        self.carrier.enable_fixed_over = False
        assert self._get_shipping_amount() == self.standard_shipping_amount

    def test_order_with_minimum_amount(self):
        assert self._get_shipping_amount() == self.reduced_shipping_amount

    def test_order_over_minimum_amount(self):
        self.line.price_unit += 1
        assert self._get_shipping_amount() == self.reduced_shipping_amount

    def test_order_below_minimum_amount(self):
        self.line.price_unit -= 1
        assert self._get_shipping_amount() == self.standard_shipping_amount

    def test_free_over_amount(self):
        self.carrier.free_over = True
        self.carrier.amount = 200
        self.line.price_unit = 200
        assert self._get_shipping_amount() == 0

    def _get_shipping_amount(self):
        return self.carrier.rate_shipment(self.order)["price"]
