# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from freezegun import freeze_time
from .common import SaleOrderKitCase


class TestSaleOrderLineDeliveredQty(SaleOrderKitCase):
    def test_important_components_delivered(self):
        self.deliver_important_components()
        assert self.kit_line.qty_delivered == 1

    def test_important_components_returned(self):
        self.deliver_important_components()
        self.return_important_components()

        assert self.component_1a.rental_returned_qty == 1
        assert self.component_1b.rental_returned_qty == 2
        assert self.kit_line.qty_delivered == 1
        assert self.kit_line.rental_returned_qty == 1

    def test_important_components_partially_delivered(self):
        self.deliver_important_components_partially()
        assert self.kit_line.qty_delivered == 0

    def test_important_components_partially_returned(self):
        self.deliver_important_components()
        self.return_important_components_partially()
        assert self.component_1a.rental_returned_qty == 1
        assert self.component_1b.rental_returned_qty == 1
        assert self.kit_line.qty_delivered == 1
        assert self.kit_line.rental_returned_qty == 0

    def test_one_component_returned(self):
        self.deliver_component(self.component_1a, 1)
        self.return_component(self.component_1a, 1)
        assert self.component_1a.rental_returned_qty == 1

    def test_service_line_qty_delivered__kit_returned(self):
        number_of_days = 20
        self.deliver_important_components()
        self.return_important_components()
        self.service_1.product_uom_qty = number_of_days
        assert self.service_1.qty_delivered == number_of_days

    def test_service_line_qty_delivered__kit_not_delivered(self):
        self.deliver_component(self.component_1a, 1)
        self.service_1.product_uom_qty = 20
        assert self.service_1.qty_delivered == 0

    def test_service_line_qty_delivered__kit_not_returned(self):
        number_of_days_since_start = 10
        date_from = datetime.now() - timedelta(number_of_days_since_start)
        self.deliver_important_components()
        self.service_1.product_uom_qty = 20
        self.service_1.rental_date_from = date_from
        assert self.service_1.qty_delivered == number_of_days_since_start + 1

    def test_service_line_qty_delivered__date_from_in_future(self):
        self.deliver_important_components()
        self.service_1.product_uom_qty = 20
        self.service_1.rental_date_from = datetime.now() + timedelta(10)
        assert self.service_1.qty_delivered == 0

    def test_service_line_qty_delivered_cron(self):
        number_of_days_since_start = 10
        self.service_1.rental_date_from = datetime.now()
        self.service_1.product_uom_qty = 20

        self.deliver_important_components()

        future_date = datetime.now() + timedelta(number_of_days_since_start)
        with freeze_time(future_date):
            self._run_service_line_qty_delivered_cron()

        assert self.service_1.qty_delivered == number_of_days_since_start + 1

    def _run_service_line_qty_delivered_cron(self):
        cron = self.env.ref("sale_rental.rental_service_qty_delivered_update_cron")
        cron.method_direct_trigger()
