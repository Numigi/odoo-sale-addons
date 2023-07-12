# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import KitCase


class TestDeliveredQty(KitCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.kit_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": cls.kit.id,
                "name": "Kit",
                "product_uom_qty": 1,
                "product_uom": cls.unit.id,
                "is_kit": True,
                "kit_reference": "K1",
            }
        )
        cls.important_component_1 = cls._make_component_line(
            "K1", cls.component_a, 2, True
        )
        cls.important_component_2 = cls._make_component_line(
            "K1", cls.component_b, 4, True
        )
        cls.optional_component = cls._make_component_line(
            "K1", cls.component_z, 10, False
        )

        cls.kit_line.copy({"order_id": cls.order.id, "kit_reference": "K2"})
        cls._make_component_line("K2", cls.component_a, 10, True)
        cls._make_component_line("K2", cls.component_b, 10, True)
        cls._make_component_line("K2", cls.component_z, 10, False)

        cls.order.action_confirm()

    @classmethod
    def _make_component_line(cls, kit_reference, product, qty, important):
        return cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": product.id,
                "name": product.display_name,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "is_kit_component": True,
                "is_important_kit_component": important,
                "kit_reference": kit_reference,
            }
        )

    def _deliver_component(self, sale_line, qty):
        move = sale_line.move_ids.filtered(lambda m: m.state != "done")[0]
        move._set_quantity_done(qty)
        move._action_done()

    def test_no_component_delivered(self):
        assert self.kit_line.qty_delivered == 0

    def test_link_between_kit_and_components(self):
        assert self.kit_line.kit_line_ids == (
            self.important_component_1
            | self.important_component_2
            | self.optional_component
        )

    def test_important_components_delivered(self):
        self._deliver_component(self.important_component_1, 2)
        assert self.kit_line.qty_delivered == 1

    def test_important_components_partially_delivered(self):
        self._deliver_component(self.important_component_1, 1)
        assert self.kit_line.qty_delivered == 0.5

    def test_second_important_component_delivered(self):
        self._deliver_component(self.important_component_2, 4)
        assert self.kit_line.qty_delivered == 0
