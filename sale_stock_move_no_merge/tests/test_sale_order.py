# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestOneStepRoute(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.salesman = cls.env["res.users"].create(
            {
                "name": "Salesman",
                "login": "test_salesman",
                "email": "test_salesman@test.com",
                "groups_id": [(4, cls.env.ref("sales_team.group_sale_salesman").id)],
            }
        )

        cls.product = cls.env["product.product"].create(
            {"name": "My Product", "type": "product"}
        )

        cls.customer = cls.env["res.partner"].create({"name": "My Customer"})

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "user_id": cls.salesman.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

        cls.sale_order.warehouse_id.delivery_steps = "pick_pack_ship"

        cls.qty_1 = 1
        cls.qty_2 = 2

        cls.line_1 = cls._create_sale_order_line(cls.sale_order, cls.product, cls.qty_1)
        cls.line_2 = cls._create_sale_order_line(cls.sale_order, cls.product, cls.qty_2)

    @classmethod
    def _create_sale_order_line(cls, order, product, quantity):
        return cls.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": product.id,
                "name": product.display_name,
                "product_uom": product.uom_id.id,
                "product_uom_qty": quantity,
            }
        )

    def test_one_delivery_move_per_sale_line(self):
        self._confirm_sale_order()
        move_1 = self.line_1.move_ids
        move_2 = self.line_2.move_ids
        assert len(move_1) == 1
        assert len(move_2) == 1
        assert move_1 != move_2

    def test_one_pack_move_per_sale_line(self):
        self._confirm_sale_order()
        move_1 = self.line_1.move_ids.move_orig_ids
        move_2 = self.line_2.move_ids.move_orig_ids
        assert len(move_1) == 1
        assert len(move_2) == 1
        assert move_1 != move_2

    def test_one_pick_move_per_sale_line(self):
        self._confirm_sale_order()
        move_1 = self.line_1.move_ids.move_orig_ids.move_orig_ids
        move_2 = self.line_2.move_ids.move_orig_ids.move_orig_ids
        assert len(move_1) == 1
        assert len(move_2) == 1
        assert move_1 != move_2

    def _confirm_sale_order(self):
        self.sale_order.sudo(self.salesman).action_confirm()
