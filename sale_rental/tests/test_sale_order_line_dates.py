# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo.addons.sale_kit.tests.common import KitCase


class TestSaleOrderKitDates(KitCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.user.partner_id.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "is_rental": True,
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
        cls.component_1a = cls._make_component_line("K1", cls.component_a, 1, True)
        cls.component_1b = cls._make_component_line("K1", cls.component_b, 2, True)
        cls.component_1z = cls._make_component_line("K1", cls.component_z, 10, False)

        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.rental_service = cls.env["product.product"].create(
            {
                "name": "My Rental Service",
                "type": "service",
                "uom_id": cls.uom_day.id,
                "uom_po_id": cls.uom_day.id,
            }
        )
        cls.service_1 = cls._make_service_line("K1", cls.rental_service, None, None, 1)

        cls.kit_line.copy({"order_id": cls.order.id, "kit_reference": "K2"})
        cls.component_2a = cls._make_component_line("K2", cls.component_a, 1, True)

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

    @classmethod
    def _make_service_line(cls, kit_reference, product, date_from, date_to, qty):
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

    def _deliver_component(self, sale_line, qty):
        candidat_moves = sale_line.move_ids.filtered(
            lambda m: m.is_rental_move() and not m.is_processed_move()
        )
        self._process_move(candidat_moves[0], qty)

    def _return_component(self, sale_line, qty):
        candidat_moves = sale_line.move_ids.filtered(
            lambda m: m.is_rental_return_move() and not m.is_processed_move()
        )
        self._process_move(candidat_moves[0], qty)

    def _process_move(self, move, qty):
        move._set_quantity_done(qty)
        move._action_done()

    def test_rental_date_from_propagated_to_kit_lines(self):
        date_from = datetime.now() + timedelta(10)
        date_to = datetime.now() + timedelta(20)
        self.service_1.rental_date_from = date_from
        self.service_1.rental_date_to = date_to

        assert self.component_1a.expected_rental_date == date_from
        assert self.component_1b.expected_rental_date == date_from
        assert self.component_1z.expected_rental_date == date_from
        assert not self.component_2a.expected_rental_date

        assert self.component_1a.expected_return_date == date_to
        assert self.component_1b.expected_return_date == date_to
        assert self.component_1z.expected_return_date == date_to
        assert not self.component_2a.expected_return_date

    def test_add_component_to_kit(self):
        date_from = datetime.now() + timedelta(10)
        date_to = datetime.now() + timedelta(20)
        self.service_1.rental_date_from = date_from
        self.service_1.rental_date_to = date_to
        new_component = self._make_component_line("K1", self.component_z, 10, False)
        assert new_component.expected_rental_date == date_from
        assert new_component.expected_return_date == date_to

    def test_add_service_to_kit(self):
        date_from = datetime.now() + timedelta(10)
        date_to = datetime.now() + timedelta(20)
        self._make_service_line("K2", self.rental_service, date_from, date_to, 1)
        assert self.component_2a.expected_rental_date == date_from
        assert self.component_2a.expected_return_date == date_to

    def test_important_components_delivered(self):
        self._deliver_component(self.component_1a, 1)
        self._deliver_component(self.component_1b, 2)
        assert self.kit_line.qty_delivered == 1

    def test_important_components_returned(self):
        self._deliver_component(self.component_1a, 1)
        self._deliver_component(self.component_1b, 2)
        self._return_component(self.component_1a, 1)
        self._return_component(self.component_1b, 2)
        assert self.component_1a.rental_returned_qty == 1
        assert self.component_1b.rental_returned_qty == 2
        assert self.kit_line.qty_delivered == 1
        assert self.kit_line.rental_returned_qty == 1

    def test_important_components_partially_delivered(self):
        self._deliver_component(self.component_1a, 1)
        self._deliver_component(self.component_1b, 1)
        assert self.kit_line.qty_delivered == 0

    def test_important_components_partially_returned(self):
        self._deliver_component(self.component_1a, 1)
        self._deliver_component(self.component_1b, 2)
        self._return_component(self.component_1a, 1)
        self._return_component(self.component_1b, 1)
        assert self.component_1a.rental_returned_qty == 1
        assert self.component_1b.rental_returned_qty == 1
        assert self.kit_line.qty_delivered == 1
        assert self.kit_line.rental_returned_qty == 0

    def test_one_component_returned(self):
        self._deliver_component(self.component_1a, 1)
        self._return_component(self.component_1a, 1)
        assert self.component_1a.rental_returned_qty == 1

    def test_service_line_qty_delivered__kit_returned(self):
        number_of_days = 20
        self._deliver_component(self.component_1a, 1)
        self._deliver_component(self.component_1b, 2)
        self._return_component(self.component_1a, 1)
        self._return_component(self.component_1b, 2)
        self.service_1.product_uom_qty = number_of_days
        assert self.service_1.qty_delivered == number_of_days

    def test_service_line_qty_delivered__kit_not_delivered(self):
        self._deliver_component(self.component_1a, 1)
        self.service_1.product_uom_qty = 20
        assert self.service_1.qty_delivered == 0

    def test_service_line_qty_delivered__kit_not_returned(self):
        number_of_days_since_start = 10
        date_from = datetime.now() - timedelta(number_of_days_since_start)
        self._deliver_component(self.component_1a, 1)
        self._deliver_component(self.component_1b, 2)
        self.service_1.product_uom_qty = 20
        self.service_1.rental_date_from = date_from
        assert self.service_1.qty_delivered == number_of_days_since_start + 1

    def test_service_line_qty_delivered__date_from_in_future(self):
        self._deliver_component(self.component_1a, 1)
        self._deliver_component(self.component_1b, 2)
        self.service_1.product_uom_qty = 20
        self.service_1.rental_date_from = datetime.now() + timedelta(10)
        assert self.service_1.qty_delivered == 0
