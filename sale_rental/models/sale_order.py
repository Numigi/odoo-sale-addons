# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from collections import defaultdict
from odoo import api, fields, models


class SaleOrderWithIsRental(models.Model):

    _inherit = 'sale.order'

    is_rental = fields.Boolean(
        'Is Rental', related='type_id.is_rental', readonly=True, store=True)


class SaleOrderWithComputeRental(models.Model):

    _inherit = 'sale.order'

    def compute_rental(self):
        required_rental_days = self._get_required_rental_days()
        rental_days = self._get_rental_days()

        for product, quantity in required_rental_days.items():
            missing_days = quantity - rental_days[product]

            editable_rental_lines = self.order_line.filtered(
                lambda l: l.product_id == product and not l.qty_invoiced)

            if editable_rental_lines:
                rental_line = editable_rental_lines[0]
                rental_line.product_uom_qty += missing_days
            else:
                rental_line = self._add_rental_line(product, days=missing_days)

    def _get_required_rental_days(self):
        required_rental_days = defaultdict(int)

        rented_product_lines = self.order_line.filtered(
            lambda l: l.product_id.rental_ok and l.product_id.rental_product_id)

        for line in rented_product_lines:
            rental_product = line.product_id.rental_product_id
            required_rental_days[rental_product] += line._get_number_of_rental_days()

        return required_rental_days

    def _get_rental_days(self):
        rental_days = defaultdict(int)

        rental_products = self.order_line.mapped('product_id.rental_product_id')
        rental_lines = self.order_line.filtered(lambda l: l.product_id in rental_products)

        for line in rental_lines:
            rental_days[line.product_id] += line.product_uom_qty

        return rental_days

    def _add_rental_line(self, product, days):
        uom_day = self.env.ref('product.product_uom_day')

        rental_line = self.env['sale.order.line'].new({
            'product_id': product.id,
            'name': '/',
            'product_uom_id': uom_day.id,
            'product_uom_qty': 0,
        })
        rental_line.product_id_change()

        rental_line.product_uom_qty = days
        rental_line.product_uom = uom_day
        rental_line.product_uom_change()

        self.order_line |= rental_line


class SaleOrderWithComputeRentalOnOrderLineChange(models.Model):

    _inherit = 'sale.order'

    @api.onchange('order_line', 'is_rental')
    def _onchange_order_line_compute_rental(self):
        if self.is_rental:
            self.compute_rental()
