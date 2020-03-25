# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo.tests.common import SavepointCase


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.user.partner_id.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "is_rental": True,
                "warehouse_id": cls.warehouse.id,
            }
        )

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

        cls.order.action_confirm()

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

    def test_rental_move_product(self):
        rental_move_1 = self._get_rental_move(self.line_1)
        assert rental_move_1.product_id == self.product_1

        rental_move_2 = self._get_rental_move(self.line_2)
        assert rental_move_2.product_id == self.product_2

    def test_return_move_product(self):
        return_move_1 = self._get_return_move(self.line_1)
        assert return_move_1.product_id == self.product_1

        return_move_2 = self._get_return_move(self.line_2)
        assert return_move_2.product_id == self.product_2

    def test_expected_rental_date(self):
        rental_move_1 = self._get_rental_move(self.line_1)
        assert rental_move_1.date_expected == self.date_start_1

        rental_move_2 = self._get_rental_move(self.line_2)
        assert rental_move_2.date_expected == self.date_start_2

    def test_expected_return_date(self):
        return_move_1 = self._get_return_move(self.line_1)
        assert return_move_1.date_expected == self.date_end_1

        return_move_2 = self._get_return_move(self.line_2)
        assert return_move_2.date_expected == self.date_end_2

    def test_change_rental_dates(self):
        new_date_start = datetime.now() + timedelta(30)
        new_date_end = datetime.now() + timedelta(60)
        self.line_1.write(
            {
                "expected_rental_date": new_date_start,
                "expected_return_date": new_date_end,
            }
        )

        rental_move_1 = self._get_rental_move(self.line_1)
        assert rental_move_1.date_expected == new_date_start

        return_move_1 = self._get_return_move(self.line_1)
        assert return_move_1.date_expected == new_date_end

    def test_if_no_expected_return_date__rental_date_used(self):
        new_date_start = datetime.now() + timedelta(30)
        self.line_1.write(
            {"expected_rental_date": new_date_start, "expected_return_date": False}
        )

        rental_move_1 = self._get_rental_move(self.line_1)
        assert rental_move_1.date_expected == new_date_start

        return_move_1 = self._get_return_move(self.line_1)
        assert return_move_1.date_expected == new_date_start

    def test_if_no_expected_rental_date__today_used(self):
        today = datetime.now().date()
        self.line_1.write(
            {"expected_rental_date": False, "expected_return_date": False}
        )

        rental_move_1 = self._get_rental_move(self.line_1)
        assert rental_move_1.date_expected.date() == today

        return_move_1 = self._get_return_move(self.line_1)
        assert return_move_1.date_expected.date() == today

    def _get_rental_move(self, sale_line):
        return sale_line.move_ids.filtered(
            lambda m: m.location_dest_id == self.customer_location
        )

    def _get_return_move(self, sale_line):
        return sale_line.move_ids.filtered(
            lambda m: m.location_dest_id == self.rental_location
        )
