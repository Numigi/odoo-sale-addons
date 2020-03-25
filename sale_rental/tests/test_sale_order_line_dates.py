# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data, unpack
from datetime import datetime, timedelta
from .common import SaleOrderKitCase


@ddt
class TestSaleOrderLineDeliveredQty(SaleOrderKitCase):
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
        new_component = self.make_component_line("K1", self.component_z, 10, False)
        assert new_component.expected_rental_date == date_from
        assert new_component.expected_return_date == date_to

    def test_add_service_to_kit(self):
        date_from = datetime.now() + timedelta(10)
        date_to = datetime.now() + timedelta(20)
        self.make_service_line("K2", self.rental_service, date_from, date_to, 1)
        assert self.component_2a.expected_rental_date == date_from
        assert self.component_2a.expected_return_date == date_to

    @data(
        (datetime(2020, 1, 1), datetime(2020, 1, 1, 23, 59, 59), 1),
        (datetime(2020, 1, 1), datetime(2020, 1, 2), 2),
        (datetime(2020, 1, 1), datetime(2020, 1, 2, 23, 59, 59), 2),
        (datetime(2020, 1, 1), datetime(2020, 1, 3), 3),
    )
    @unpack
    def test_onchange_rental_dates(self, date_from, date_to, quantity):
        self.service_1.rental_date_from = date_from
        self.service_1.rental_date_to = date_to
        self.service_1.onchange_rental_dates()
        assert self.service_1.product_uom_qty == quantity

    def test_onchange_rental_dates__date_to_forced_after_date_from(self):
        date_from = datetime(2020, 1, 3)
        self.service_1.rental_date_from = date_from
        self.service_1.rental_date_to = datetime(2020, 1, 1)
        self.service_1.onchange_rental_dates()
        assert self.service_1.rental_date_to == date_from
        assert self.service_1.product_uom_qty == 1
