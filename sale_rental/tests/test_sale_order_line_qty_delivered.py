# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from freezegun import freeze_time
from .common import SaleOrderKitCase, RentalCase


# class TestKitRental(SaleOrderKitCase):
#     def test_important_components_delivered(self):
#         self.deliver_important_components()
#         assert self.kit_line.qty_delivered == 1
#         assert self.kit_line.rental_returned_qty == 0
#
#     def test_important_components_returned(self):
#         self.deliver_important_components()
#         self.return_important_components()
#
#         assert self.component_1a.rental_returned_qty == 2
#         assert self.component_1b.rental_returned_qty == 4
#         assert self.kit_line.qty_delivered == 1
#         assert self.kit_line.rental_returned_qty == 1
#
#     def test_important_components_partially_delivered(self):
#         self.deliver_important_components_partially()
#         assert self.kit_line.qty_delivered == 0.5
#
#     def test_important_components_partially_returned(self):
#         self.deliver_important_components()
#         self.return_important_components_partially()
#         assert self.component_1a.rental_returned_qty == 1
#         assert self.component_1b.rental_returned_qty == 2
#         assert self.kit_line.qty_delivered == 1
#         assert self.kit_line.rental_returned_qty == 0
#
#     def test_one_component_returned(self):
#         self.deliver_product(self.component_1a, 1)
#         self.return_product(self.component_1a, 1)
#         assert self.component_1a.rental_returned_qty == 1
#
#     def test_service_line_qty_delivered__kit_returned(self):
#         number_of_days = 20
#         self.deliver_important_components()
#         self.return_important_components()
#         self.service_1.product_uom_qty = number_of_days
#         assert self.service_1.qty_delivered == number_of_days
#
#     def test_service_line_qty_delivered__kit_not_fully_delivered(self):
#         self.deliver_product(self.component_1a, 1)
#         self.service_1.product_uom_qty = 20
#         assert self.service_1.qty_delivered == 0
#
#     def test_service_line_qty_delivered__kit_not_returned(self):
#         number_of_days_since_start = 10
#         date_from = datetime.now() - timedelta(number_of_days_since_start)
#         self.deliver_important_components()
#         self.service_1.product_uom_qty = 20
#         self.service_1.rental_date_from = date_from
#         assert self.service_1.qty_delivered == number_of_days_since_start + 1
#
#     def test_service_line_qty_delivered__date_from_in_future(self):
#         self.deliver_important_components()
#         self.service_1.product_uom_qty = 20
#         self.service_1.rental_date_from = datetime.now() + timedelta(10)
#         assert self.service_1.qty_delivered == 0
#
#     def test_service_line_qty_delivered_cron(self):
#         number_of_days_since_start = 10
#         self.service_1.rental_date_from = datetime.now()
#         self.service_1.product_uom_qty = 20
#
#         self.deliver_important_components()
#
#         future_date = datetime.now() + timedelta(number_of_days_since_start)
#         with freeze_time(future_date):
#             self._run_service_line_qty_delivered_cron()
#
#         assert self.service_1.qty_delivered == number_of_days_since_start + 1
#
#     def _run_service_line_qty_delivered_cron(self):
#         cron = self.env.ref("sale_rental.rental_service_qty_delivered_update_cron")
#         cron.method_direct_trigger()
#
#
# class TestNonKitRental(RentalCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.product_line = cls.env["sale.order.line"].create(
#             {
#                 "order_id": cls.order.id,
#                 "product_id": cls.component_a.id,
#                 "name": cls.component_a.display_name,
#                 "product_uom_qty": 1,
#                 "product_uom": cls.unit.id,
#                 "is_kit": True,
#                 "kit_reference": "K1",
#             }
#         )
#
#         cls.service_line = cls.make_service_line(
#             "K1", cls.rental_service, None, None, 1
#         )
#         cls.order.action_confirm()
#
#     def test_product_not_delivered(self):
#         assert self.product_line.qty_delivered == 0
#         assert self.service_line.qty_delivered == 0
#         assert self.product_line.rental_returned_qty == 0
#         assert self.service_line.rental_returned_qty == 0
#
#     def test_product_delivered(self):
#         self.deliver_product(self.product_line, 1)
#         assert self.product_line.qty_delivered == 1
#         assert self.service_line.qty_delivered == 1
#         assert self.product_line.rental_returned_qty == 0
#         assert self.service_line.rental_returned_qty == 0
#
#     def test_product_returned(self):
#         self.deliver_product(self.product_line, 1)
#         self.return_product(self.product_line, 1)
#         assert self.product_line.qty_delivered == 1
#         assert self.product_line.rental_returned_qty == 1
#         assert self.service_line.rental_returned_qty == 0
#
#     def test_service_line_qty_delivered__product_returned(self):
#         number_of_days = 20
#         self.deliver_product(self.product_line, 1)
#         self.return_product(self.product_line, 1)
#         self.service_line.product_uom_qty = number_of_days
#         assert self.service_line.qty_delivered == number_of_days
#
#     def test_service_line_qty_delivered__product_not_delivered(self):
#         self.service_line.product_uom_qty = 20
#         assert self.service_line.qty_delivered == 0
#
#     def test_service_line_qty_delivered__product_not_returned(self):
#         number_of_days_since_start = 10
#         date_from = datetime.now() - timedelta(number_of_days_since_start)
#         self.deliver_product(self.product_line, 1)
#         self.service_line.product_uom_qty = 20
#         self.service_line.rental_date_from = date_from
#         assert self.service_line.qty_delivered == number_of_days_since_start + 1
#
#
# class TestDuplicatedRentalSaleOrder(TestNonKitRental):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.deliver_product(cls.product_line, 1)
#         cls.return_product(cls.product_line, 1)
#         cls.order = cls.order.copy()
#         cls.product_line = cls.order.order_line[0]
#         cls.service_line = cls.order.order_line[1]
#         cls.order.action_confirm()
