# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from collections import defaultdict
from odoo import api, fields, models


class SaleOrderWithIsRental(models.Model):
    """Add a boolean field to identify rental sales.

    When selecting a type of sale order checked as rental, two new columns
    are added to the sale order lines:

        * Rental Date
        * Expected Return Date

    These columns are reserved for rental sale order and should not be used
    otherwise.
    """

    _inherit = 'sale.order'

    is_rental = fields.Boolean(
        'Is Rental', related='type_id.is_rental', readonly=True, store=True)


class SaleOrderWithComputeRental(models.Model):
    """Add a method to automatically compute the rental sale order lines."""

    _inherit = 'sale.order'

    def compute_rental(self):
        """Compute the rental service lines based on the rented product lines.

        Whatever the state of the sale order, this method updates the lines
        of the sale order to add missing rental service lines based on rental
        products.
        """
        required_rental_days = self._get_required_rental_days()

        current_rental_days = self._get_current_rental_days()
        unrequired_rental_days = [
            (k, v) for k, v in current_rental_days.items()
            if k not in required_rental_days
        ]

        for product, quantity in required_rental_days.items():
            missing_days = quantity - current_rental_days[product]
            self._update_rental_days(product, missing_days)

        for product, quantity in unrequired_rental_days:
            self._update_rental_days(product, -quantity)

    def _get_required_rental_days(self):
        """Get the required days of rental per service product.

        :returns: a defaultdict of integers containing the required rental services days.
        """
        required_rental_days = defaultdict(int)

        rented_product_lines = self.order_line.filtered(
            lambda l: l.product_id.rental_ok and l.product_id.rental_product_id)

        for line in rented_product_lines:
            rental_product = line.product_id.rental_product_id
            required_rental_days[rental_product] += line._get_number_of_rental_days()

        return required_rental_days

    def _get_current_rental_days(self):
        """Get the days of rental per service product currently written on the sale order.

        :returns: a defaultdict of integers containing the current rental services days.
        """
        rental_days = defaultdict(int)

        rental_lines = self.order_line.filtered(lambda l: l.product_id.is_rental)

        for line in rental_lines:
            rental_days[line.product_id] += line.product_uom_qty

        return rental_days

    def _update_rental_days(self, product, days):
        """Update the number of rental days for a given rental service product.

        :param product: the rental service
        :param days: the number of days to add (or remove if negative)
        """
        editable_rental_lines = self.order_line.filtered(
            lambda l: l.product_id == product and not l.qty_invoiced)

        if editable_rental_lines:
            rental_line = editable_rental_lines[0]
            rental_line.product_uom_qty += days

            if not rental_line.product_uom_qty:
                self.order_line -= rental_line
        else:
            self._add_rental_line(product, days=days)

    def _add_rental_line(self, product, days):
        """Add a new rental line for a given rental product with the given number of days.

        :param product: the rental service to add
        :param days: the number of days of the line to add
        """
        uom_day = self.env.ref('product.product_uom_day')

        self.order_line |= self.env['sale.order.line'].new({
            'product_id': product.id,
            'name': '/',
            'product_uom_id': uom_day.id,
            'product_uom_qty': 0,
        })
        rental_line = self.order_line.filtered(
            lambda l: l.product_id == product and not l.qty_invoiced)[0]
        rental_line.product_id_change()

        rental_line.product_uom_qty = days
        rental_line.product_uom = uom_day
        rental_line.product_uom_change()


class SaleOrderWithComputeRentalOnOrderLineChange(models.Model):

    _inherit = 'sale.order'

    @api.onchange('order_line', 'is_rental')
    def _onchange_order_line_compute_rental(self):
        if self.is_rental:
            self.compute_rental()
