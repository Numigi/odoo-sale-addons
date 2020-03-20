# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class KitCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.unit = cls.env.ref("uom.product_uom_unit")
        cls.dozen = cls.env.ref("uom.product_uom_dozen")

        cls.tax = cls.env["account.tax"].create(
            {"name": "Test Tax", "amount": 10, "amount_type": "fixed"}
        )

        cls.component_a = cls.env["product.product"].create(
            {"name": "Component A", "type": "consu", "taxes_id": [(4, cls.tax.id)]}
        )
        cls.component_b = cls.env["product.product"].create(
            {"name": "Component B", "type": "consu", "taxes_id": [(4, cls.tax.id)]}
        )
        cls.component_z = cls.env["product.product"].create(
            {
                "name": "Component Z (Non-important)",
                "type": "consu",
                "taxes_id": [(4, cls.tax.id)],
            }
        )

        cls.component_a_uom = cls.dozen
        cls.component_b_uom = cls.unit
        cls.component_z_uom = cls.unit

        cls.component_a_qty = 1
        cls.component_b_qty = 2
        cls.component_z_qty = 3

        component_a_vals = cls.get_kit_line_vals(
            cls.component_a, cls.component_a_qty, cls.component_a_uom, True
        )
        component_b_vals = cls.get_kit_line_vals(
            cls.component_b, cls.component_b_qty, cls.component_b_uom, True
        )
        component_z_vals = cls.get_kit_line_vals(
            cls.component_z, cls.component_z_qty, cls.component_z_uom, False
        )

        cls.kit = cls.env["product.product"].create(
            {
                "name": "My Kit",
                "type": "service",
                "is_kit": True,
                "taxes_id": [(4, cls.tax.id)],
                "kit_line_ids": [
                    (0, 0, component_a_vals),
                    (0, 0, component_b_vals),
                    (0, 0, component_z_vals),
                ],
            }
        )

    @staticmethod
    def get_kit_line_vals(product, qty, uom, important):
        return {
            "component_id": product.id,
            "quantity": qty,
            "uom_id": uom.id,
            "is_important": important,
        }


class SaleOrderLineCase(KitCase):
    def setUp(self):
        super().setUp()
        self.order = self.env["sale.order"].new(
            {
                "partner_id": self.env.user.partner_id.id,
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )

    @classmethod
    def new_so_line(cls, vals=None):
        return cls.env["sale.order.line"].new(vals or {})

    def add_kit_on_sale_order(self):
        kit_line = self.new_so_line()
        kit_line.is_rental_order = self.order.is_rental
        self.select_product(kit_line, self.kit)
        self.order.order_line |= kit_line
        kit_line.order_id = self.order
        self.order.initialize_kits()
        return kit_line

    @staticmethod
    def select_product(line, product):
        line.product_id = product
        line.product_id_change()

    def get_kit_lines(self):
        return self.order.order_line.filtered(lambda l: l.is_kit)

    def get_component_lines(self):
        return self.order.order_line.filtered(lambda l: l.is_kit_component)
