# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.sale_rental.tests.test_sale_order_line import KitRentalCase


class TestSaleRentalOrderSwapVariant(KitRentalCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.component_a_1 = cls.env["product.product"].create(
            {
                "name": "Component A 1",
                "type": "product",
                "product_tmpl_id": cls.component_a.product_tmpl_id.id,
            }
        )
        cls.kit.kit_line_ids.filtered(lambda r: r.is_important).write(
            {"allow_change_variant": True}
        )
        so_env = cls.env["sale.order"]
        sol_env = cls.env["sale.order.line"]
        cls.so = so_env.create(
            {
                "partner_id": cls.env.user.partner_id.id,
                "is_rental": True,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.kit_line = sol_env.create({"order_id": cls.so.id, "product_id": cls.kit.id})
        cls.kit_line.is_rental_order = cls.so.is_rental
        cls.kit_line.product_id_change()
        cls.kit_line.initialize_kit()
        cls.so.action_confirm()
        cls.change_variant_sol = cls.so.order_line.filtered(
            lambda r: r.allow_change_variant_kit_component
        )[0]
        cls.wizard_env = cls.env["sale.rental.order.swap.variant"].with_context(
            active_model="sale.order.line",
            active_id=cls.change_variant_sol.id,
            default_active_product_id=cls.change_variant_sol.product_id.id,
        )

    def test_wizard_action_replace_before_stock_move_done(self):
        self._change_variant()
        self.assertEqual(self.change_variant_sol.product_id, self.component_a_1)
        stock_moves = self._get_all_stock_moves().filtered(
            lambda m: m.state != "cancel"
        )
        self.assertEqual(stock_moves.mapped("product_id"), self.component_a_1)

    def test_old_stock_moves_are_cancelled(self):
        old_moves = self._get_all_stock_moves()
        self._change_variant()
        assert all(m.state == "cancel" for m in old_moves)
        assert all(not m.picking_id for m in old_moves)

    def _get_all_stock_moves(self):
        delivery_moves = self.change_variant_sol.move_ids
        return_moves = delivery_moves.mapped("move_dest_ids")
        return delivery_moves | return_moves

    def test_test_wizard_action_replace_after_stock_move_done(self):
        picking = self.so.picking_ids[0]
        picking.move_ids_without_package.write({"quantity_done": 1})
        picking.button_validate()
        self.change_variant_sol.move_ids._action_done()
        with self.assertRaises(ValidationError):
            self._change_variant()

    def _change_variant(self):
        with Form(self.wizard_env) as wizard_form:
            wizard_form.product_id = self.component_a_1
            res = wizard_form.save()
            res.change_variant()
