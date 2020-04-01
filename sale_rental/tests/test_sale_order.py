# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from .common import RentalCase


class SaleOrderCase(RentalCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Product 2", "type": "product"}
        )

        now = datetime.now()
        cls.date_start_1 = now + timedelta(1)
        cls.date_start_2 = now + timedelta(2)
        cls.date_end_1 = now + timedelta(7)
        cls.date_end_2 = now + timedelta(8)

        cls.line_1 = cls._make_sale_order_line(
            cls.product_1, 1, cls.date_start_1, cls.date_end_1
        )
        cls.line_2 = cls._make_sale_order_line(
            cls.product_2, 2, cls.date_start_2, cls.date_end_2
        )

        cls.customer_location = cls.env.ref("sale_rental.customer_location")
        cls.rental_location = cls.warehouse.rental_location_id

    @classmethod
    def _make_sale_order_line(cls, product, qty, date_start, date_end):
        return cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": product.id,
                "name": product.display_name,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "expected_rental_date": date_start,
                "expected_return_date": date_end,
            }
        )

    def get_rental_move(self, sale_line):
        return sale_line.move_ids.filtered(
            lambda m: m.location_dest_id == self.customer_location
        )

    def get_return_move(self, sale_line):
        return sale_line.move_ids.filtered(
            lambda m: m.location_dest_id == self.rental_location
        )


class TestSaleOrder(SaleOrderCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order.action_confirm()

    def test_rental_move_product(self):
        rental_move_1 = self.get_rental_move(self.line_1)
        assert rental_move_1.product_id == self.product_1

        rental_move_2 = self.get_rental_move(self.line_2)
        assert rental_move_2.product_id == self.product_2

    def test_return_move_product(self):
        return_move_1 = self.get_return_move(self.line_1)
        assert return_move_1.product_id == self.product_1

        return_move_2 = self.get_return_move(self.line_2)
        assert return_move_2.product_id == self.product_2

    def test_expected_rental_date(self):
        rental_move_1 = self.get_rental_move(self.line_1)
        assert rental_move_1.date_expected == self.date_start_1

        rental_move_2 = self.get_rental_move(self.line_2)
        assert rental_move_2.date_expected == self.date_start_2

    def test_expected_return_date(self):
        return_move_1 = self.get_return_move(self.line_1)
        assert return_move_1.date_expected == self.date_end_1

        return_move_2 = self.get_return_move(self.line_2)
        assert return_move_2.date_expected == self.date_end_2

    def test_expected_date_not_propagated_to_return_move(self):
        rental_move_1 = self.get_rental_move(self.line_1)
        return_move_1 = self.get_return_move(self.line_1)

        rental_move_1.date_expected = datetime.now() + timedelta(100)
        assert return_move_1.date_expected == self.date_end_1

    def test_change_rental_dates(self):
        new_date_start = datetime.now() + timedelta(30)
        new_date_end = datetime.now() + timedelta(60)
        self.line_1.write(
            {
                "expected_rental_date": new_date_start,
                "expected_return_date": new_date_end,
            }
        )

        rental_move_1 = self.get_rental_move(self.line_1)
        assert rental_move_1.date_expected == new_date_start

        return_move_1 = self.get_return_move(self.line_1)
        assert return_move_1.date_expected == new_date_end

    def test_if_no_expected_return_date__rental_date_used(self):
        new_date_start = datetime.now() + timedelta(30)
        self.line_1.write(
            {"expected_rental_date": new_date_start, "expected_return_date": False}
        )

        rental_move_1 = self.get_rental_move(self.line_1)
        assert rental_move_1.date_expected == new_date_start

        return_move_1 = self.get_return_move(self.line_1)
        assert return_move_1.date_expected == new_date_start

    def test_if_no_expected_rental_date__today_used(self):
        today = datetime.now().date()
        self.line_1.write(
            {"expected_rental_date": False, "expected_return_date": False}
        )

        rental_move_1 = self.get_rental_move(self.line_1)
        assert rental_move_1.date_expected.date() == today

        return_move_1 = self.get_return_move(self.line_1)
        assert return_move_1.date_expected.date() == today

    def test_return_picking_excluded_from_delivery_count(self):
        assert self.order.delivery_count == 1

    def test_action_view_delivery(self):
        action = self.order.action_view_delivery()
        picking = self.env["stock.picking"].search(action["domain"])
        assert picking.location_dest_id == self.customer_location

    def test_rental_return_count(self):
        assert self.order.rental_return_count == 1

    def test_action_view_rental_return_pickings(self):
        action = self.order.action_view_rental_return_pickings()
        picking = self.env["stock.picking"].search(action["domain"])
        assert picking.location_dest_id == self.rental_location


class TestSaleOrderMultipleSteps(SaleOrderCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._add_second_pull_rule()
        cls._add_second_push_rule()
        cls.order.action_confirm()

    @classmethod
    def _add_second_pull_rule(cls):
        route = cls.warehouse.rental_route_id
        pull_rule = route.rule_ids.filtered(lambda r: r.action == "pull")
        pull_rule.copy(
            {
                "location_src_id": cls.warehouse.lot_stock_id.id,
                "location_id": cls.rental_location.id,
            }
        )
        pull_rule.procure_method = "make_to_order"

    @classmethod
    def _add_second_push_rule(cls):
        route = cls.warehouse.rental_route_id
        push_rule = route.rule_ids.filtered(lambda r: r.action == "push")
        push_rule.copy(
            {
                "location_src_id": cls.rental_location.id,
                "location_id": cls.warehouse.lot_stock_id.id,
            }
        )

    def test_rental_return_count(self):
        assert self.order.delivery_count == 2
        assert self.order.rental_return_count == 2

    def test_expected_rental_date__propagated_to_second_pull_move(self):
        first_pull = self.get_rental_move(self.line_1)
        second_pull = first_pull.move_orig_ids
        assert second_pull.date_expected == self.date_start_1

    def test_expected_return_date__propagated_to_second_push_move(self):
        first_push = self.get_rental_move(self.line_1)
        second_push = first_push.move_dest_ids
        assert second_push.date_expected == self.date_end_1
