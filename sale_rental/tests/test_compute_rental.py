# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta

from odoo.tests.common import SavepointCase


class TestComputeRental(SavepointCase):

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
        })

        cls.rental_product_b = cls.env['product.product'].create({
            'name': 'Rental Service B',
            'type': 'service',
            'uom_id': cls.uom_day.id,
            'uom_po_id': cls.uom_day.id,
            'is_rental': True,
        })

        cls.product_a = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'rental_ok': True,
            'rental_product_id': cls.rental_product_a.id,
        })

        cls.product_b = cls.env['product.product'].create({
            'name': 'Product B',
            'type': 'product',
            'rental_ok': True,
            'rental_product_id': cls.rental_product_b.id,
        })

        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.env.ref('base.res_partner_1').id,
        })

    def _add_rented_product_line(self, product, quantity, days):
        date_from = datetime.now().date()
        date_to = date_from + timedelta(days=days)

        self.order.write({
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': product.name,
                'product_uom_qty': quantity,
                'rental_date_from': date_from,
                'rental_date_to': date_to,
            })]
        })

    def _get_rental_lines(self, rental_product):
        return self.order.order_line.filtered(lambda l: l.product_id == rental_product)

    def _compute_rental(self):
        self.order.compute_rental()
        self.order.refresh()
        self.order.order_line.refresh()

    def test_onComputeRental_ifNoSaleLine_thenNoRentalProductIsAdded(self):
        self.order.compute_rental()
        self.assertEqual(len(self.order.order_line), 0)

    def test_onComputeRental_ifOneRentedProduct_thenOneRentalLineIsAdded(self):
        self._add_rented_product_line(self.product_a, quantity=1, days=1)
        self._compute_rental()

        self.assertEqual(len(self.order.order_line), 2)

        rental_line = self._get_rental_lines(self.rental_product_a)
        self.assertEqual(len(rental_line), 1)
        self.assertEqual(rental_line.product_uom_qty, 1)
        self.assertEqual(rental_line.product_uom, self.uom_day)

    def test_onComputeRental_ifTwoDifferentRentedProduct_thenTwoRentalLinesAreAdded(self):
        self._add_rented_product_line(self.product_a, quantity=1, days=1)
        self._add_rented_product_line(self.product_b, quantity=1, days=1)
        self._compute_rental()

        self.assertEqual(len(self.order.order_line), 4)

        line_a = self._get_rental_lines(self.rental_product_a)
        self.assertEqual(len(line_a), 1)
        self.assertEqual(line_a.product_uom_qty, 1)
        self.assertEqual(line_a.product_uom, self.uom_day)

        line_b = self._get_rental_lines(self.rental_product_b)
        self.assertEqual(len(line_b), 1)
        self.assertEqual(line_b.product_uom_qty, 1)
        self.assertEqual(line_b.product_uom, self.uom_day)

    def test_onComputeRental_thenNumberOfRentalDaysIsComputedCorrectly(self):
        self._add_rented_product_line(self.product_a, quantity=2, days=3)
        self._compute_rental()

        self.assertEqual(len(self.order.order_line), 2)

        rental_line = self._get_rental_lines(self.rental_product_a)
        self.assertEqual(rental_line.product_uom_qty, 6)  # 2 units * 3 days
        self.assertEqual(rental_line.product_uom, self.uom_day)

    def test_onComputeRental_withExistingRentalLine_thenNoSaleLineIsAdded(self):
        self._add_rented_product_line(self.product_a, quantity=2, days=3)
        self.order._add_rental_line(self.rental_product_a, days=4)
        self._compute_rental()

        self.assertEqual(len(self.order.order_line), 2)

        rental_line = self._get_rental_lines(self.rental_product_a)
        self.assertEqual(rental_line.product_uom_qty, 6)  # 2 units * 3 days

    def test_onComputeRental_withTwoExistingRentalLine_thenNoSaleLineIsAdded(self):
        self._add_rented_product_line(self.product_a, quantity=2, days=3)
        self.order._add_rental_line(self.rental_product_a, days=1)
        self.order._add_rental_line(self.rental_product_a, days=2)
        self._compute_rental()

        self.assertEqual(len(self.order.order_line), 3)

        rental_line = self._get_rental_lines(self.rental_product_a)
        self.assertEqual(sum(rental_line.mapped('product_uom_qty')), 6)  # 2 units * 3 days

    def test_onComputeRental_thenUnitPriceIsSetOnRentalLine(self):
        self._add_rented_product_line(self.product_a, quantity=2, days=3)

        self.rental_product_a.list_price = 10
        self._compute_rental()

        self.assertEqual(len(self.order.order_line), 2)

        rental_line = self._get_rental_lines(self.rental_product_a)
        self.assertEqual(rental_line.price_unit, 10)

    def test_onComputeRental_thenUnrequiredRentalLinesAreEmptied(self):
        self._add_rented_product_line(self.product_a, quantity=2, days=3)
        self._compute_rental()

        self.assertEqual(len(self.order.order_line), 2)
        self.assertTrue(self._get_rental_lines(self.rental_product_a))

        # Replace product a with product b
        self.order.order_line.filtered(lambda l: l.product_id == self.product_a).unlink()
        self._add_rented_product_line(self.product_b, quantity=2, days=3)

        self._compute_rental()
        self.assertEqual(len(self.order.order_line), 2)
        self.assertTrue(self._get_rental_lines(self.rental_product_b))
        self.assertFalse(self._get_rental_lines(self.rental_product_a))
