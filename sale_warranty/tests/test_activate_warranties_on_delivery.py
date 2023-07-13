# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
from .common import WarrantyActivationCase


class TestWarrantyActivatedOnDelivery(WarrantyActivationCase):

    def test_on_delivery_serial_number_is_propagated_to_warranty(self):
        self.confirm_sale_order()
        serial_1 = self.generate_serial_number(self.product_a, '000001')

        picking = self.sale_order.picking_ids
        self.select_serial_numbers_on_picking(picking, serial_1)
        self.validate_picking(picking)

        warranty = self.sale_order.warranty_ids
        assert warranty.state == 'active'
        assert warranty.lot_id == serial_1
        warranty_ids = serial_1.get_warranties()
        assert warranty_ids in serial_1.sale_order_ids.mapped(
            "warranty_ids")
        assert serial_1.warranty_count == 1

        # And if adding new warranty to the SN
        today = datetime.now().date()
        warranty_2 = self.env['sale.warranty'].create({
            'partner_id': self.customer.id,
            'product_id': self.product_a.id,
            'type_id': self.warranty_6_months.id,
            'activation_date': today,
            'lot_id': serial_1.id,
            'expiry_date': today + timedelta(30),
        })
        assert warranty_2.id != warranty.id
        assert warranty_2.lot_id == warranty.lot_id
        serial_1.refresh()
        assert serial_1.warranty_count == 2

    def test_on_back_order_serial_number_is_propagated_to_warranty(self):
        self.sale_order.order_line.product_uom_qty = 3
        self.confirm_sale_order()

        first_picking = self.sale_order.picking_ids
        serial_1 = self.generate_serial_number(self.product_a, '000001')
        serial_2 = self.generate_serial_number(self.product_a, '000002')
        self.select_serial_numbers_on_picking(
            first_picking, serial_1 | serial_2)
        self.validate_picking(first_picking)

        active_warranties = self.sale_order.warranty_ids.filtered(
            lambda w: w.state == 'active')
        assert len(active_warranties) == 2
        assert active_warranties.mapped('lot_id') == serial_1 | serial_2

        back_order = self.sale_order.picking_ids - first_picking
        serial_3 = self.generate_serial_number(self.product_a, '000003')
        self.select_serial_numbers_on_picking(back_order, serial_3)
        self.validate_picking(back_order)

        active_warranties = self.sale_order.warranty_ids.filtered(
            lambda w: w.state == 'active')
        assert len(active_warranties) == 3
        assert active_warranties.mapped(
            'lot_id') == serial_1 | serial_2 | serial_3

    def test_on_delivery_activation_date_set_to_delivery_date(self):
        self.confirm_sale_order()

        delivery_date = datetime.now().date() + timedelta(30)
        expected_expiry_date = delivery_date + \
            relativedelta(months=6) - timedelta(1)

        with freeze_time(delivery_date):
            picking = self.sale_order.picking_ids
            serial_1 = self.generate_serial_number(self.product_a, '000001')
            self.select_serial_numbers_on_picking(picking, serial_1)
            self.validate_picking(picking)

        warranty = self.sale_order.warranty_ids
        assert warranty.activation_date == delivery_date
        assert warranty.expiry_date == expected_expiry_date

    def test_warranty_activation_without_serial_number(self):
        self.warranty_6_months.allow_non_serialized_products = True
        self.product_a.tracking = 'none'
        self.add_product_to_stock(self.product_a, 1)

        self.confirm_sale_order()

        picking = self.sale_order.picking_ids
        self.select_product_on_picking(picking, self.product_a, 1)
        self.validate_picking(picking)

        warranty = self.sale_order.warranty_ids
        assert warranty.state == 'active'
        assert not warranty.lot_id
