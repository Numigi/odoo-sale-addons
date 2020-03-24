# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from .common import SaleOrderKitCase


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
