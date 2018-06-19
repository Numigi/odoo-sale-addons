# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from freezegun import freeze_time
from datetime import datetime, timedelta

from odoo import fields
from odoo.tests.common import SavepointCase

date_to_string = fields.Date.to_string


class TestReturnRental(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.uom_day = cls.env.ref('product.product_uom_day')

        cls.rental_product_a = cls.env['product.product'].create({
            'name': 'Rental Service A',
            'type': 'service',
            'uom_id': cls.uom_day.id,
            'uom_po_id': cls.uom_day.id,
            'is_rental': True,
            'list_price': 30,
        })

        cls.product_a = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'rental_ok': True,
            'rental_product_id': cls.rental_product_a.id,
            'tracking': 'serial',
        })

        cls.sn_1 = cls.env['stock.production.lot'].create({
            'product_id': cls.product_a.id,
            'name': 'SN1',
        })

        cls.sn_2 = cls.env['stock.production.lot'].create({
            'product_id': cls.product_a.id,
            'name': 'SN2',
        })

        cls.sn_3 = cls.env['stock.production.lot'].create({
            'product_id': cls.product_a.id,
            'name': 'SN3',
        })

        cls.today = date_to_string(datetime.now().date())
        cls.four_days_later = date_to_string(datetime.now().date() + timedelta(days=4))
        cls.seven_days_later = date_to_string(datetime.now().date() + timedelta(days=7))

        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.env.ref('base.res_partner_1').id,
            'type_id': cls.env.ref('sale_rental.sale_order_type_rental').id,
            'order_line': [(0, 0, {
                'product_id': cls.product_a.id,
                'name': cls.product_a.name,
                'product_uom_qty': 3,
                'rental_date_from': cls.today,
                'rental_date_to': cls.seven_days_later,
            })],
        })
        cls.order.compute_rental()
        cls.order.action_confirm()

        cls.delivery = cls.order.picking_ids

        cls._transfer_rental_picking(cls.delivery)

        cls.rented_product_line = cls.order.order_line.filtered(
            lambda l: l.product_id == cls.product_a)

    @classmethod
    def _transfer_rental_picking(cls, picking):
        picking.force_assign()

        move = picking.move_lines

        for sn in [cls.sn_1, cls.sn_2, cls.sn_3]:
            move.move_line_ids |= cls.env['stock.move.line'].create(dict(
                move._prepare_move_line_vals(), qty_done=1, lot_id=sn.id))

        picking.action_done()

    def _return_serial_numbers(self, serial_numbers):
        wizard_fields = [
            'product_return_moves',
            'move_dest_exists',
            'parent_location_id',
            'original_location_id',
            'location_id',
        ]
        wizard_defaults = (
            self.env['stock.return.picking']
            .with_context(active_id=self.delivery.id).default_get(wizard_fields)
        )
        wizard = self.env['stock.return.picking'].create(wizard_defaults)
        wizard.product_return_moves.quantity = len(serial_numbers)
        wizard.product_return_moves.to_refund = True

        return_picking_id = wizard.create_returns()['res_id']
        return_picking = self.env['stock.picking'].browse(return_picking_id)

        move = return_picking.move_lines

        for sn in serial_numbers:
            move.move_line_ids |= self.env['stock.move.line'].create(dict(
                move._prepare_move_line_vals(), qty_done=1, lot_id=sn.id))

        with freeze_time(self.four_days_later):
            return_picking.action_done()

        return return_picking

    def test_whenProductIsReturned_thenReturnMoveIsLinkedToRentalMove(self):
        self.assertEqual(self.rented_product_line.qty_delivered, 3)

        return_picking = self._return_serial_numbers(self.sn_1)
        self.assertEqual(self.rented_product_line.qty_delivered, 2)

        delivery_line_1 = self.delivery.move_line_ids.filtered(lambda l: l.lot_id == self.sn_1)
        return_line_1 = return_picking.move_line_ids.filtered(lambda l: l.lot_id == self.sn_1)

        self.assertTrue(return_line_1)
        self.assertEqual(delivery_line_1.rental_return_id, return_line_1)

    def test_whenTwoProductsAreReturned_thenEachReturnedMoveIsLinkedToTheProperRentalMove(self):
        self.assertEqual(self.rented_product_line.qty_delivered, 3)

        return_picking = self._return_serial_numbers(self.sn_1 | self.sn_3)
        self.assertEqual(self.rented_product_line.qty_delivered, 1)

        delivery_line_1 = self.delivery.move_line_ids.filtered(lambda l: l.lot_id == self.sn_1)
        delivery_line_3 = self.delivery.move_line_ids.filtered(lambda l: l.lot_id == self.sn_3)

        return_line_1 = return_picking.move_line_ids.filtered(lambda l: l.lot_id == self.sn_1)
        return_line_3 = return_picking.move_line_ids.filtered(lambda l: l.lot_id == self.sn_3)

        self.assertTrue(return_line_1)
        self.assertTrue(return_line_3)

        self.assertEqual(delivery_line_1.rental_return_id, return_line_1)
        self.assertEqual(delivery_line_3.rental_return_id, return_line_3)

    def test_whenProductIsReturned_thenRentalDateToIsTheDateOfTheReturn(self):
        delivery_line_1 = self.delivery.move_line_ids.filtered(lambda l: l.lot_id == self.sn_1)

        # Before returning the product, the rental date to is the expected date of return.
        self.assertEqual(delivery_line_1.rental_date_to, self.seven_days_later)

        self._return_serial_numbers(self.sn_1)

        # After returning the product, the rental date to is the effective date of return.
        self.assertEqual(delivery_line_1.rental_date_to, self.four_days_later)
