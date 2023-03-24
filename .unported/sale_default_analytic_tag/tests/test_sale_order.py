# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.tests.common import SavepointCase


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag_1 = cls.env["account.analytic.tag"].create(
            {
                "name": "Tag 1",
            }
        )
        cls.tag_2 = cls.env["account.analytic.tag"].create(
            {
                "name": "Tag 2",
            }
        )
        cls.product = cls.env["product.product"].create({"name": "My Product"})
        cls.product.sale_analytic_tag_ids = [(6, 0, [cls.tag_1.id, cls.tag_2.id])]

    def setUp(self):
        super().setUp()
        self.order = self.env["sale.order"].new(
            {
                "partner_id": self.env.user.partner_id.id,
            }
        )

        self.line = self.env["sale.order.line"].new(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
            }
        )

    def test_onchange_product(self):
        self.line.product_id_change()
        assert self.line.analytic_tag_ids._origin == self.tag_1 | self.tag_2
