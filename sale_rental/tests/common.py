# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.sale_kit.tests.common import KitCase


class RentalCase(KitCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Set queue job to no delay for testing
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        cls.stock_user = cls.env.ref("base.user_demo")
        cls.stock_user.groups_id = cls.env.ref("stock.group_stock_user")

        cls.partner = cls.env.ref("base.res_partner_1")

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.rental_service = cls.env["product.product"].create(
            {
                "name": "My Rental Service",
                "type": "service",
                "uom_id": cls.uom_day.id,
                "uom_po_id": cls.uom_day.id,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "is_rental": True,
            }
        )

    @classmethod
    def make_component_line(cls, kit_reference, product, qty, important):
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

    @classmethod
    def make_service_line(cls, kit_reference, product, date_from, date_to, qty):
        return cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": product.id,
                "name": "Rental",
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "kit_reference": kit_reference,
                "rental_date_from": date_from,
                "rental_date_to": date_to,
                "is_rental_service": True,
            }
        )

    @classmethod
    def deliver_product(cls, sale_line, qty=None):
        if qty is None:
            qty = sale_line.product_uom_qty

        candidat_moves = sale_line.move_ids.filtered(
            lambda m: m.is_rental_move() and not m.is_processed_move()
        )
        cls.process_move(candidat_moves[0], qty)

    @classmethod
    def return_product(cls, sale_line, qty=None):
        if qty is None:
            qty = sale_line.product_uom_qty

        candidat_moves = sale_line.move_ids.filtered(
            lambda m: m.is_rental_return_move() and not m.is_processed_move()
        )
        cls.process_move(candidat_moves[0], qty)

    @classmethod
    def process_move(cls, move, qty):
        move._set_quantity_done(qty)
        move.sudo(cls.stock_user)._action_done()


class SaleOrderKitCase(RentalCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

        cls.component_1a = cls.make_component_line("K1", cls.component_a, 2, True)
        cls.component_1b = cls.make_component_line("K1", cls.component_b, 4, True)
        cls.component_1z = cls.make_component_line("K1", cls.component_z, 10, False)

        cls.service_1 = cls.make_service_line("K1", cls.rental_service, None, None, 1)

        cls.kit_line.copy({"order_id": cls.order.id, "kit_reference": "K2"})
        cls.component_2a = cls.make_component_line("K2", cls.component_a, 1, True)

        cls.order.action_confirm()

    @classmethod
    def deliver_important_components(cls):
        cls.deliver_product(cls.component_1a, 2)
        cls.deliver_product(cls.component_1b, 4)

    @classmethod
    def deliver_important_components_partially(cls):
        cls.deliver_product(cls.component_1a, 1)
        cls.deliver_product(cls.component_1b, 2)

    @classmethod
    def return_important_components(cls):
        cls.return_product(cls.component_1a, 2)
        cls.return_product(cls.component_1b, 4)

    @classmethod
    def return_important_components_partially(cls):
        cls.return_product(cls.component_1a, 1)
        cls.return_product(cls.component_1b, 2)
