# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager
from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.sale_kit.tests.common import KitCase


class TestSaleKit(KitCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.kit_line = cls.env["sale.order.line"].create(
            {"order_id": cls.order.id, "product_id": cls.kit.id}
        )
        cls.kit_line.product_id_change()
        cls.kit_line.initialize_kit()
        cls.order.action_confirm()
        cls.order_line = cls.order.order_line[1]
        cls.env["res.lang"].load_lang("fr_FR")

    def test_wizard_action_replace_before_stock_move_done(self):
        self._change_variant()
        self.assertEqual(self.order_line.product_id, self.component_b)
        stock_moves = self._get_all_stock_moves().filtered(
            lambda m: m.state != "cancel"
        )
        self.assertEqual(stock_moves.mapped("product_id"), self.component_b)

    def test_old_stock_moves_are_cancelled(self):
        old_moves = self._get_all_stock_moves()
        self._change_variant()
        assert all(m.state == "cancel" for m in old_moves)
        assert all(not m.picking_id for m in old_moves)

    def test_draft_sale_order__no_stock_moves_created(self):
        self.order.state = "draft"
        self._change_variant()
        lines = self._get_all_stock_moves().filtered(lambda m: m.state != "cancel")
        assert not lines

    def _get_all_stock_moves(self):
        delivery_moves = self.order_line.move_ids
        return_moves = delivery_moves.mapped("move_dest_ids")
        return delivery_moves | return_moves

    def test_test_wizard_action_replace_after_stock_move_done(self):
        picking = self.order.picking_ids[0]
        picking.move_ids_without_package.write({"quantity_done": 1})
        picking.button_validate()
        self.order_line.move_ids._action_done()
        with self.assertRaises(ValidationError):
            self._change_variant()

    def test_product_description_is_in_partner_lang(self):
        fr_term = "Mon Article"
        self.order.partner_id.lang = "fr_FR"
        self.component_b.with_context(lang="fr_FR").name = fr_term
        self._change_variant()
        assert fr_term in self.order_line.name

    def test_change_product_uom_qty(self):
        new_quantity = 999
        with self._open_wizard() as wizard:
            wizard.quantity = new_quantity
            wizard.change_variant()

        assert self.order_line.product_uom_qty == new_quantity

    def test_button_visible(self):
        self.order_line.allow_change_product = True
        assert self.order_line.change_variant_button_visible

    def test_button_visible__change_variant_allowed(self):
        self.order_line.allow_change_variant = True
        assert self.order_line.change_variant_button_visible

    def test_button_invisible(self):
        assert not self.order_line.change_variant_button_visible

    def test_button_invisible__order_done(self):
        self.order_line.allow_change_product = True
        self.order.state = "done"
        assert not self.order_line.change_variant_button_visible

    def _change_variant(self):
        with self._open_wizard() as wizard:
            wizard.change_variant()

    @contextmanager
    def _open_wizard(self):
        wizard_env = self.env["sale.rental.order.swap.variant"].with_context(
            default_sale_line_id=self.order_line.id,
        )

        with Form(wizard_env) as wizard_form:
            wizard_form.product_id = self.component_b
            wizard = wizard_form.save()
            yield wizard
