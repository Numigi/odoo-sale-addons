# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.sale_kit.tests.common import SaleOrderLineCase


class TestKitComponentSorting(SaleOrderLineCase):
    def setUp(self):
        super().setUp()
        self.k1 = self.new_so_line({"kit_reference": "K1", "is_kit": True})
        self.k1_1 = self.new_so_line(
            {"kit_reference": "K1", "is_important_kit_component": True}
        )
        self.k1_2 = self.new_so_line({"kit_reference": "K1"})
        self.k1_rental = self.new_so_line(
            {"kit_reference": "K1", "is_rental_service": True}
        )
        self.k2 = self.new_so_line({"kit_reference": "K2", "is_kit": True})

        self.order.is_rental = True
        self.order.order_line = (
            self.k1 | self.k1_1 | self.k1_2 | self.k1_rental | self.k2
        )

    def test_sort_kit_lines(self):
        self.order.update_kit_component_sequences()
        assert [l for l in self.order.order_line] == [
            self.k1,
            self.k1_rental,
            self.k1_1,
            self.k1_2,
            self.k2,
        ]

    def test_component_with_sequence_smaller_than_rental_service(self):
        self.k1_2.sequence = -1
        self.k1.sequence = 1
        self.k1_rental.sequence = 2
        self.k1_1.sequence = 3
        self.k2.sequence = 4
        self.order.update_kit_component_sequences()
        assert [l for l in self.order.order_line] == [
            self.k1,
            self.k1_rental,
            self.k1_1,
            self.k1_2,
            self.k2,
        ]
