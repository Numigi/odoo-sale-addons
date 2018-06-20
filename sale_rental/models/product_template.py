# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplateWithRentalOK(models.Model):
    """Add a checkbox field to identify products that can be rented."""

    _inherit = 'product.template'

    rental_ok = fields.Boolean('Can be Rented', track_visibility='onchange')


class ProductTemplateWithRentalOkMustHaveUnitUom(models.Model):
    """Prevent rental of products in custom units of measure."""

    _inherit = 'product.template'

    @api.constrains('uom_id', 'uom_po_id', 'rental_ok')
    def _check_rentable_product_has_unit_uom(self):
        rentable_products = self.filtered(lambda l: l.rental_ok)
        uom_unit = self.env.ref('product.product_uom_unit')

        for product in rentable_products:
            if product.uom_id != uom_unit or product.uom_po_id != uom_unit:
                raise ValidationError(_(
                    '{product} can be rented. '
                    'Therefore, its unit of measure must be {uom_unit}.'
                ).format(product=product, uom_unit=uom_unit.display_name))

    @api.onchange('rental_ok')
    def _onchange_rental_ok_set_uom_unit(self):
        if self.rental_ok:
            uom_unit = self.env.ref('product.product_uom_unit')
            self.uom_id = uom_unit
            self.uom_po_id = uom_unit


class ProductTemplateWithRentalOKMustBeStockableProduct(models.Model):
    """Rented products must be stockable products.

    For a service or a software, a subscription module should be more appropriate.
    """

    _inherit = 'product.template'

    @api.constrains('type', 'rental_ok')
    def _check_rentable_product_must_be_a_stockable_product(self):
        rentable_products = self.filtered(lambda l: l.rental_ok)

        for product in rentable_products:
            if product.type != 'product':
                raise ValidationError(_(
                    '{product} can be rented. Therefore, it must be a stockable product.'
                ).format(product=product))

    @api.onchange('rental_ok')
    def _onchange_rental_ok_set_type_to_stockable_product(self):
        if self.rental_ok:
            self.type = 'product'


class ProductTemplateWithRentalOKMustBeTrackedBySerialNumber(models.Model):
    """A product that can be rented must be tracked with a serial number.

    A rental system without mandatory tracking would be much more complicate to
    implement because the tracking is what makes the link between the delivered
    and returned products.
    """

    _inherit = 'product.template'

    @api.constrains('tracking', 'rental_ok')
    def _check_rentable_product_is_tracked_with_serial_number(self):
        rentable_products = self.filtered(lambda l: l.rental_ok)

        for product in rentable_products:
            if product.tracking != 'serial':
                raise ValidationError(_(
                    '{product} can be rented. Therefore, it must be tracked with a serial number.'
                ).format(product=product))

    @api.onchange('rental_ok')
    def _onchange_rental_ok_set_tracking_with_serial_number(self):
        if self.rental_ok:
            self.tracking = 'serial'


class ProductTemplateWithIsRental(models.Model):
    """Add a checkbox field to identify rental products.

    A rental product is used to invoice the price per day of a rented product.

    On a sale order, there is one line for the rented stockable product (uom == units)
    and one line for the rental service (uom == days).
    """

    _inherit = 'product.template'

    is_rental = fields.Boolean('Is A Rental Service', track_visibility='onchange')


class ProductTemplateWithIsRentalMustBeService(models.Model):
    """Check that rental products are services."""

    _inherit = 'product.template'

    @api.constrains('type', 'is_rental')
    def _check_rental_product_must_be_a_service(self):
        rental_products = self.filtered(lambda l: l.is_rental)

        for product in rental_products:
            if product.type != 'service':
                raise ValidationError(_(
                    '{product} is a rental product. Therefore, it must be a service.'
                ).format(product=product))

    @api.onchange('type')
    def _onchange_type_if_not_service_then_empty_is_rental(self):
        if self.type != 'service':
            self.is_rental = False


class ProductTemplateWithIsRentalMustHaveDayUom(models.Model):
    """Prevent using other units of measure then days for rental services.

    Allowing other time units of measure would make the module much more
    complicate and error prone.

    There is no plan on supporting monthly or hourly units of measure in
    the future, even if a use case is listed.
    """

    _inherit = 'product.template'

    @api.constrains('uom_id', 'uom_po_id', 'is_rental')
    def _check_rental_product_has_day_uom(self):
        rental_products = self.filtered(lambda l: l.is_rental)
        uom_day = self.env.ref('product.product_uom_day')

        for product in rental_products:
            if product.uom_id != uom_day or product.uom_po_id != uom_day:
                raise ValidationError(_(
                    '{product} is a rental product. '
                    'Therefore, its unit of measure must be {uom_day}.'
                ).format(product=product, uom_day=uom_day.display_name))

    @api.onchange('is_rental')
    def _onchange_is_rental_set_days_as_product_uom(self):
        if self.is_rental:
            uom_day = self.env.ref('product.product_uom_day')
            self.uom_id = uom_day
            self.uom_po_id = uom_day


class ProductTemplateWithRentalProduct(models.Model):
    """Add a relation between the rented product and the rental service."""

    _inherit = 'product.template'

    rental_product_id = fields.Many2one(
        'product.product', 'Rental Product', ondelete='restrict',
        track_visibility='onchange')

    @api.constrains('rental_product_id')
    def _check_rental_product_id_is_rental_product(self):
        """Verify that the rental service is checked as a rental service."""
        products_with_rental_products = self.filtered(lambda p: p.rental_product_id)

        for product in products_with_rental_products:
            if not product.rental_product_id.is_rental:
                raise ValidationError(_(
                    'The rental service {service} on the product {product} '
                    'must be tagged as a rental service.'
                ).format(service=product.rental_product_id.display_name,
                         product=product.display_name))
