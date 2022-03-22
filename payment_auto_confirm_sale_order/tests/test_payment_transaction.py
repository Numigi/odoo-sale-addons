# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestPayment(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Product A"})

        cls.customer = cls.env["res.partner"].create(
            {"name": "My Customer", "customer": True}
        )

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.line = cls._create_sale_order_line(cls.order)

        cls.acquirer = cls.env.ref("payment.payment_acquirer_transfer")
        cls.acquirer.auto_confirm_sale_order = "confirm_order"

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

    def test_order_auto_confirmed(self):
        self._create_payment_transaction()
        assert self.order.state == "sale"

    def test_order_not_auto_confirmed(self):
        self.acquirer.auto_confirm_sale_order = False
        self._create_payment_transaction()
        assert self.order.state == "draft"

    def test_quotation_sent(self):
        self.acquirer.auto_confirm_sale_order = "send_quotation"
        self._create_payment_transaction()
        assert self.order.state == "sent"

    def _create_payment_transaction(self):
        return self.order._create_payment_transaction({"acquirer_id": self.acquirer.id})
