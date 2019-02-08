# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
from odoo.tests.common import SavepointCase


class TestSaleWarranty(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.salesman = cls.env['res.users'].create({
            'name': 'Salesman',
            'login': 'test_salesman',
            'email': 'test_salesman@test.com',
            'groups_id': [(4, cls.env.ref('sales_team.group_sale_salesman').id)]
        })

        cls.stock_user = cls.env['res.users'].create({
            'name': 'Stock User',
            'login': 'test_stock_user',
            'email': 'test_stock_user@test.com',
            'groups_id': [(4, cls.env.ref('stock.group_stock_user').id)]
        })

        cls.warranty_6_months = cls.env['sale.warranty.type'].create({
            'name': '6 Months Parts',
            'duration_in_months': 6,
            'description': 'Warranted 6 months on parts'
        })

        cls.warranty_2_years = cls.env['sale.warranty.type'].create({
            'name': '2 Years Parts',
            'duration_in_months': 24,
            'description': 'Warranted 2 years on parts'
        })

        cls.product_a = cls.env['product.product'].create({
            'name': 'My Product',
            'tracking': 'serial',
            'type': 'product',
            'warranty_type_ids': [(4, cls.warranty_6_months.id)]
        })

        cls.product_b = cls.env['product.product'].create({
            'name': 'My Product B',
            'tracking': 'serial',
            'type': 'product',
            'warranty_type_ids': [(4, cls.warranty_2_years.id)]
        })

        cls.customer = cls.env['res.partner'].create({
            'name': 'My Customer',
            'customer': True,
        })

        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'user_id': cls.salesman.id,
            'order_line': [
                (0, 0, {
                    'product_id': cls.product_a.id,
                    'name': cls.product_a.name,
                    'product_uom': cls.env.ref('uom.product_uom_unit').id,
                    'product_uom_qty': 1,
                })
            ]
        })

    def _confirm_sale_order(self):
        self.sale_order.sudo(self.salesman).action_confirm()

    def _generate_serial_number(self, product, number):
        serial = self.env['stock.production.lot'].create({
            'number': number,
            'product_id': product.id,
        })
        inventory = self.env['stock.inventory'].create({
            'name': 'Add serial number',
        })
        inventory.action_start()

        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', self.env.user.company_id.id),
        ])
        inventory.write({
            'line_ids': [(0, 0, {
                'product_id': product.id,
                'product_qty': 1,
                'prod_lot_id': serial.id,
                'location_id': warehouse.lot_stock_id.id,
            })]
        })
        inventory.action_validate()
        return serial

    def test_on_sale_order_confirm_warranty_is_created(self):
        self._confirm_sale_order()
        warranty = self.sale_order.warranty_ids
        assert len(warranty) == 1
        assert warranty.state == 'pending'
        assert warranty.product_id == self.product_a
        assert warranty.type_id == self.warranty_6_months
        assert warranty.description == self.warranty_6_months.description
        assert warranty.sale_order_line_id == self.sale_order.order_line
        assert warranty.partner_id == self.customer

    def test_one_warranty_created_per_product_unit(self):
        self.sale_order.order_line.product_uom_qty = 3
        self._confirm_sale_order()
        assert len(self.sale_order.warranty_ids) == 3

    def test_if_product_not_warranteed_no_warranty_created(self):
        self.product_a.warranty_type_ids = False
        self._confirm_sale_order()
        assert not self.sale_order.warranty_ids

    def test_if_product_has_multiple_warranties_then_each_warranty_created(self):
        self.product_a.warranty_type_ids = self.warranty_6_months | self.warranty_2_years
        self.sale_order.order_line.product_uom_qty = 3
        self._confirm_sale_order()
        assert len(self.sale_order.warranty_ids) == 6

    def test_on_add_extra_order_line_extra_warranty_is_added(self):
        self._confirm_sale_order()
        assert len(self.sale_order.warranty_ids) == 1

        self.sale_order.write({
            'order_line': [
                (0, 0, {
                    'product_id': self.product_b.id,
                    'name': self.product_b.name,
                    'product_uom': self.env.ref('uom.product_uom_unit').id,
                    'product_uom_qty': 1,
                })
            ]
        })

        warranties = self.sale_order.warranty_ids.sorted(key=lambda w: w.id)
        sale_lines = self.sale_order.order_line.sorted(key=lambda l: l.id)
        assert len(warranties) == 2
        assert warranties[0].sale_order_line_id == sale_lines[0]
        assert warranties[1].sale_order_line_id == sale_lines[1]

    def test_on_add_extra_quantity_then_extra_warranty_is_added(self):
        self._confirm_sale_order()
        assert len(self.sale_order.warranty_ids) == 1
        self.sale_order.order_line.product_uom_qty = 2
        assert len(self.sale_order.warranty_ids) == 2

    def test_on_cancel_order_then_warranties_cancelled(self):
        self._confirm_sale_order()
        assert self.sale_order.warranty_ids.state == 'pending'
        self.sale_order.action_cancel()
        assert self.sale_order.warranty_ids.state == 'cancelled'

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
