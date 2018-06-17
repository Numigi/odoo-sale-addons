# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLineWithIsRentedProduct(models.Model):

    _inherit = 'sale.order.line'

    is_rented_product = fields.Boolean(
        'Is Rented Product', compute='_compute_is_rented_product', readonly=True, store=True)

    @api.depends('order_id.is_rental', 'product_id.rental_ok')
    def _compute_is_rented_product(self):
        for line in self:
            line.is_rented_product = line.order_id.is_rental and line.product_id.rental_ok


class SaleOrderLineWithIsRental(models.Model):

    _inherit = 'sale.order.line'

    is_rental = fields.Boolean(
        'Is Rental', related='product_id.is_rental', readonly=True, store=True)


class SaleOrderLineWithRentalDates(models.Model):

    _inherit = 'sale.order.line'

    rental_date_from = fields.Date('Rental Date')
    rental_date_to = fields.Date('Expected Return Date')

    def _get_number_of_rental_days(self):
        if not self.rental_date_from or not self.rental_date_to:
            return 0

        rental_date_from = fields.Date.from_string(self.rental_date_from)
        rental_date_to = fields.Date.from_string(self.rental_date_to)

        return max((rental_date_to - rental_date_from).days, 0) * self.product_uom_qty

    @api.constrains('rental_date_from', 'rental_date_to')
    def _check_rental_date_from_is_not_after_rental_date_to(self):
        for line in self:
            if (
                line.rental_date_from and line.rental_date_to and
                line.rental_date_from > line.rental_date_to
            ):
                raise ValidationError(_(
                    'The order line {line} can not have a date of rental {date_from} '
                    'after its expected date of return {date_to}.'
                ).format(
                    line=line.display_name,
                    date_from=line.rental_date_from,
                    date_to=line.rental_date_to))
