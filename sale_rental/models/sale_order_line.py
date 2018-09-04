# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
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


class SaleOrderLineWithRentedAndReturnedQuantity(models.Model):

    _inherit = 'sale.order.line'

    rented_quantity = fields.Float(
        string='Delivered Qty', compute='_compute_rented_quantity',
        digits=dp.get_precision('Product Unit of Measure'))

    rental_returned_quantity = fields.Float(
        string='Returned Qty', compute='_compute_rented_quantity',
        digits=dp.get_precision('Product Unit of Measure'))

    @api.depends('move_ids.state')
    def _compute_rented_quantity(self):
        rented_products = self.filtered(lambda l: l.is_rented_product)

        for line in rented_products:
            line.rented_quantity = sum(
                move.quantity_done for move in line.move_ids
                if move.state == 'done' and move.location_dest_id.usage == 'customer'
            )

            line.rental_returned_quantity = sum(
                move.quantity_done for move in line.move_ids
                if move.state == 'done' and move.location_dest_id.usage != 'customer'
            )


class SaleOrderLineWithInvoiceBasedOnRentedQuantities(models.Model):
    """A rented product must be invoiced based on the ordered qty minus the returned qty."""

    _inherit = 'sale.order.line'

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state',
                 'rental_returned_quantity')
    def _get_to_invoice_qty(self):
        rented_products = self.filtered(lambda l: l.is_rented_product)

        for line in rented_products:
            if line.order_id.state in ['sale', 'done']:
                line.qty_to_invoice = (
                    line.product_uom_qty - line.rental_returned_quantity - line.qty_invoiced
                )
            else:
                line.qty_to_invoice = 0

        other_lines = self - rented_products
        super(SaleOrderLineWithInvoiceBasedOnRentedQuantities, other_lines)._get_to_invoice_qty()
