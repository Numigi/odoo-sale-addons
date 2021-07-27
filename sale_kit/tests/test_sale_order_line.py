# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data, unpack
from ..models.sale_order import extract_kit_number
from .common import SaleOrderLineCase


@ddt
class TestSaleOrderLine(SaleOrderLineCase):
    def test_if_product_is_kit__then_line_is_kit(self):
        line = self.new_so_line()
        self.select_product(line, self.kit)
        assert line.is_kit

    def test_if_product_is_not_kit__then_line_is_not_kit(self):
        line = self.new_so_line()
        self.select_product(line, self.component_a)
        assert not line.is_kit

    def test_if_product_is_kit__then_new_kit_reference(self):
        line_1 = self.add_kit_on_sale_order()
        assert line_1.kit_reference == "K1"

        line_2 = self.add_kit_on_sale_order()
        assert line_2.kit_reference == "K2"

    def test_if_product_is_not_kit__then_no_new_kit_reference(self):
        line = self.new_so_line()
        line = line.with_context(next_kit_reference="K3")
        self.select_product(line, self.component_a)
        assert not line.kit_reference

    def test_next_kit_reference__with_empty_sale_order(self):
        assert self.order.next_kit_reference == "K1"

    def test_next_kit_reference__with_existing_lines(self):
        line_1 = self.new_so_line()
        line_1.kit_reference = "K1"

        line_2 = self.new_so_line()
        line_2.kit_reference = "K3"

        with self.env.do_in_onchange():
            self.order.order_line = line_1 | line_2
            assert self.order.next_kit_reference == "K4"

    def test_available_kit_references(self):
        with self.env.do_in_onchange():
            for ref in (False, "K1", "K3", "K3", "K2"):
                line = self.new_so_line()
                line.kit_reference = ref
                self.order.order_line |= line

            assert self.order.available_kit_references == "K1,K2,K3"

    @data(("K1", 1), ("ABC999", 999), ("WRONG", 0))
    @unpack
    def test_extract_kit_number(self, ref, expected_number):
        assert extract_kit_number(ref) == expected_number

    def test_one_line_added_per_component(self):
        self.add_kit_on_sale_order()
        assert len(self.order.order_line) == 4

        self.add_kit_on_sale_order()
        assert len(self.order.order_line) == 8

    def test_products(self):
        self.add_kit_on_sale_order()
        lines = self.order.order_line
        assert lines[0].product_id == self.kit
        assert lines[1].product_id == self.component_a
        assert lines[2].product_id == self.component_b
        assert lines[3].product_id == self.component_z

    def test_is_component(self):
        self.add_kit_on_sale_order()
        lines = self.order.order_line
        assert not lines[0].is_kit_component
        assert lines[1].is_kit_component
        assert lines[2].is_kit_component
        assert lines[3].is_kit_component

    def test_is_important_kit_component(self):
        self.add_kit_on_sale_order()
        lines = self.order.order_line
        assert not lines[0].is_important_kit_component
        assert lines[1].is_important_kit_component
        assert lines[2].is_important_kit_component
        assert not lines[3].is_important_kit_component

    def test_component_quantities(self):
        self.add_kit_on_sale_order()
        lines = self.get_component_lines()
        assert len(lines) == 3
        assert lines[0].product_uom_qty == self.component_a_qty
        assert lines[1].product_uom_qty == self.component_b_qty
        assert lines[2].product_uom_qty == self.component_z_qty

    def test_component_uom(self):
        self.add_kit_on_sale_order()
        lines = self.get_component_lines()
        assert len(lines) == 3
        assert lines[0].product_uom == self.component_a_uom
        assert lines[1].product_uom == self.component_b_uom
        assert lines[2].product_uom == self.component_z_uom

    def test_component_discount(self):
        discount = 0.2
        self.kit.kit_discount = discount
        self.add_kit_on_sale_order()
        lines = self.get_component_lines()
        assert len(lines) == 3
        assert lines[0].discount == discount
        assert lines[1].discount == discount
        assert lines[2].discount == discount

    def test_kit_line__readonly_conditions(self):
        line = self.add_kit_on_sale_order()
        assert line.is_kit
        assert not line.handle_widget_invisible
        assert not line.trash_widget_invisible
        assert line.product_readonly
        assert line.product_uom_qty_readonly
        assert line.product_uom_readonly
        assert line.kit_reference_readonly

    def test_important_composant__readonly_conditions(self):
        self.add_kit_on_sale_order()
        line = self.order.order_line[1]
        assert line.is_important_kit_component
        assert line.handle_widget_invisible
        assert line.trash_widget_invisible
        assert line.product_readonly
        assert line.product_uom_qty_readonly
        assert line.product_uom_readonly
        assert line.kit_reference_readonly

    def test_non_important_composant__readonly_conditions(self):
        self.add_kit_on_sale_order()
        line = self.order.order_line[3]
        assert not line.is_important_kit_component
        assert not line.handle_widget_invisible
        assert not line.trash_widget_invisible
        assert not line.product_readonly
        assert not line.product_uom_qty_readonly
        assert not line.product_uom_readonly
        assert not line.kit_reference_readonly

    def test_if_kit_line_deleted__components_deleted(self):
        k1 = self.add_kit_on_sale_order()
        assert len(self.order.order_line) == 4

        self.add_kit_on_sale_order()
        assert len(self.order.order_line) == 8

        self.order.order_line -= k1
        self.order.unlink_dangling_kit_components()
        assert len(self.order.order_line) == 4
        assert set(self.order.order_line.mapped("kit_reference")) == {"K2"}
