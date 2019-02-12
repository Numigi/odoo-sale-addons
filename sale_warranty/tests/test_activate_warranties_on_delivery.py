# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
from .common import SaleWarrantyCase


class TestWarrantyActivatedOnDelivery(SaleWarrantyCase):

    def _select_serial_number_on_stock_picking(self, serial_number, picking):
        move = next(m for m in picking.move_lines if m.product_id == serial_number.product_id)
        move_line_vals = {
            'location_dest_id': move.location_dest_id.id,
            'location_id': move.location_id.id,
            'lot_id': serial_number.id,
            'product_id': move.product_id.id,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'qty_done': 1,
        }
        line_without_serial = next((l for l in move.move_line_ids if not l.lot_id), None)
        if line_without_serial:
            line_without_serial.write(move_line_vals)
        else:
            move.write({'move_line_ids': [(0, 0, move_line_vals)]})

    def _deliver_products(self, picking, serial_numbers):
        for serial in serial_numbers:
            self._select_serial_number_on_stock_picking(serial, picking)
        picking.sudo(self.stock_user).action_done()

        # Verify that the stock.picking was properly processed.
        assert picking.state == 'done'
        move_lines = picking.mapped('move_lines.move_line_ids')
        assert len(move_lines) == len(serial_numbers)
        assert move_lines.mapped('lot_id') == serial_numbers
        for line in move_lines:
            assert line.qty_done == 1

    def test_on_delivery_serial_number_is_propagated_to_warranty(self):
        self._confirm_sale_order()
        serial_1 = self._generate_serial_number(self.product_a, '000001')

        picking = self.sale_order.picking_ids
        self._deliver_products(picking, serial_1)

        warranty = self.sale_order.warranty_ids
        assert warranty.state == 'active'
        assert warranty.lot_id == serial_1

    def test_on_back_order_serial_number_is_propagated_to_warranty(self):
        self.sale_order.order_line.product_uom_qty = 3
        self._confirm_sale_order()

        first_picking = self.sale_order.picking_ids
        serial_1 = self._generate_serial_number(self.product_a, '000001')
        serial_2 = self._generate_serial_number(self.product_a, '000002')
        self._deliver_products(first_picking, serial_1 | serial_2)

        active_warranties = self.sale_order.warranty_ids.filtered(lambda w: w.state == 'active')
        assert len(active_warranties) == 2
        assert active_warranties.mapped('lot_id') == serial_1 | serial_2

        back_order = self.sale_order.picking_ids - first_picking
        serial_3 = self._generate_serial_number(self.product_a, '000003')
        self._deliver_products(back_order, serial_3)

        active_warranties = self.sale_order.warranty_ids.filtered(lambda w: w.state == 'active')
        assert len(active_warranties) == 3
        assert active_warranties.mapped('lot_id') == serial_1 | serial_2 | serial_3

    def test_on_delivery_activation_date_set_to_delivery_date(self):
        self._confirm_sale_order()

        delivery_date = datetime.now().date() + timedelta(30)
        expected_expiry_date = delivery_date + relativedelta(months=6) - timedelta(1)

        with freeze_time(delivery_date):
            picking = self.sale_order.picking_ids
            serial_1 = self._generate_serial_number(self.product_a, '000001')
            self._deliver_products(picking, serial_1)

        warranty = self.sale_order.warranty_ids
        assert warranty.activation_date == delivery_date
        assert warranty.expiry_date == expected_expiry_date
