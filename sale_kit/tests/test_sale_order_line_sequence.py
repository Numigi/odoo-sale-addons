# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import SaleOrderLineCase


class TestKitComponentSorting(SaleOrderLineCase):
    def setUp(self):
        super().setUp()
        self.k1 = self.new_so_line({"kit_reference": "K1", "is_kit": True})
        self.k1_1 = self.new_so_line({"kit_reference": "K1", "kit_sequence": 1})
        self.k1_2 = self.new_so_line({"kit_reference": "K1", "kit_sequence": 2})

        self.k2 = self.new_so_line({"kit_reference": "K2", "is_kit": True})
        self.k2_1 = self.new_so_line({"kit_reference": "K2", "kit_sequence": 1})
        self.k2_2 = self.new_so_line({"kit_reference": "K2", "kit_sequence": 2})

        self.other_line_1 = self.new_so_line()
        self.other_line_2 = self.new_so_line()

        self.order.order_line = (
            self.k1
            | self.k1_1
            | self.k1_2
            | self.k2
            | self.k2_1
            | self.k2_2
            | self.other_line_1
            | self.other_line_2
        )

    # def test_sort_kit_lines(self):
    #     self.k1.sequence = 1
    #     self.k2.sequence = 3
    #     self.other_line_1.sequence = 2
    #     self.other_line_2.sequence = 4
    #     self.order.update_kit_component_sequences()
    #     assert [l for l in self.order.order_line] == [
    #         self.k1,
    #         self.k1_1,
    #         self.k1_2,
    #         self.other_line_1,
    #         self.k2,
    #         self.k2_1,
    #         self.k2_2,
    #         self.other_line_2,
    #     ]
    #
    # def test_reorder_kits(self):
    #     self.k1.sequence = 4
    #     self.k2.sequence = 1
    #     self.other_line_1.sequence = 3
    #     self.other_line_2.sequence = 2
    #
    #     self.order.update_kit_component_sequences()
    #     assert [l for l in self.order.order_line] == [
    #         self.k2,
    #         self.k2_1,
    #         self.k2_2,
    #         self.other_line_2,
    #         self.other_line_1,
    #         self.k1,
    #         self.k1_1,
    #         self.k1_2,
    #     ]
    #
    # def test_component_with_sequence_lower_than_kit(self):
    #     self.k1_1.sequence = -1
    #     self.k1.sequence = 0
    #     self.k2.sequence = 1
    #     self.other_line_1.sequence = 2
    #     self.other_line_2.sequence = 3
    #
    #     self.order.update_kit_component_sequences()
    #     assert [l for l in self.order.order_line] == [
    #         self.k1,
    #         self.k1_1,
    #         self.k1_2,
    #         self.k2,
    #         self.k2_1,
    #         self.k2_2,
    #         self.other_line_1,
    #         self.other_line_2,
    #     ]
