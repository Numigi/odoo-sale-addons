# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class SaleOrderLineCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.unit = cls.env.ref("uom.product_uom_unit")

        cls.component_a = cls.env["product.product"].create(
            {"name": "Component A", "type": "consu"}
        )
        cls.component_b = cls.env["product.product"].create(
            {"name": "Component B", "type": "consu"}
        )
        cls.component_z = cls.env["product.product"].create(
            {"name": "Component Z (Non-important)", "type": "consu"}
        )

        cls.kit = cls.env["product.product"].create(
            {
                "name": "My Kit",
                "type": "service",
                "is_kit": True,
                "kit_line_ids": [
                    (0, 0, cls.get_kit_line_vals(cls.component_a, True)),
                    (0, 0, cls.get_kit_line_vals(cls.component_b, True)),
                    (0, 0, cls.get_kit_line_vals(cls.component_z, False)),
                ],
            }
        )

        cls.order = cls.env["sale.order"].new(
            {"partner_id": cls.env.user.partner_id.id}
        )

    @staticmethod
    def get_kit_line_vals(product, important):
        return {"component_id": product.id, "is_important": important}

    @classmethod
    def new_so_line(cls, vals=None):
        return cls.env["sale.order.line"].new(vals or {})

    @staticmethod
    def select_product(line, product):
        line.product_id = product
        line.product_id_change()

    @classmethod
    def add_kit_on_sale_order(cls):
        kit_line = cls.new_so_line()
        cls.select_product(kit_line, cls.kit)
        cls.order.order_line |= kit_line
        kit_line.order_id = cls.order
        cls.order.initialize_kits()
        return kit_line
