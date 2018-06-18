# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplateWithRentalOK(models.Model):

    _inherit = 'product.template'

    rental_ok = fields.Boolean('Can be Rented')

    @api.constrains('type', 'rental_ok')
    def _check_product_that_can_be_rented_must_be_a_stockable_product(self):
        rentable_products = self.filtered(lambda l: l.rental_ok)

        for product in rentable_products:
            if product.type != 'product':
                raise ValidationError(_(
                    '{product} can be rented. Therefore, it must be a stockable product.'
                ).format(product=product))

    @api.constrains('uom_id', 'uom_po_id', 'rental_ok')
    def _check_rental_product_has_day_uom(self):
        rentable_products = self.filtered(lambda l: l.rental_ok)
        uom_unit = self.env.ref('product.product_uom_unit')

        for product in rentable_products:
            if product.uom_id != uom_unit or product.uom_po_id != uom_unit:
                raise ValidationError(_(
                    '{product} can be rented. '
                    'Therefore, its unit of measure must be {uom_unit}.'
                ).format(product=product, uom_unit=uom_unit.display_name))

    @api.onchange('rental_ok')
    def _onchange_rental_ok_set_invoice_policy_to_delivered_quantity(self):
        if self.rental_ok:
            self.invoice_policy = 'delivery'

    @api.onchange('rental_ok')
    def _onchange_rental_ok_set_type_to_stockable_product(self):
        if self.rental_ok:
            self.type = 'product'


class ProductWithRentalOK(models.Model):

    _inherit = 'product.product'

    @api.onchange('rental_ok')
    def _onchange_rental_ok_set_invoice_policy_to_delivered_quantity(self):
        if self.rental_ok:
            self.invoice_policy = 'delivery'

    @api.onchange('rental_ok')
    def _onchange_rental_ok_set_type_to_stockable_product(self):
        if self.rental_ok:
            self.type = 'product'


class ProductTemplateWithIsRental(models.Model):

    _inherit = 'product.template'

    is_rental = fields.Boolean('Is A Rental Service')

    @api.constrains('type', 'is_rental')
    def _check_rental_product_must_be_a_service(self):
        rental_products = self.filtered(lambda l: l.is_rental)

        for product in rental_products:
            if product.type != 'service':
                raise ValidationError(_(
                    '{product} is a rental product. Therefore, it must be a service.'
                ).format(product=product))

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

    @api.onchange('type')
    def _onchange_type_if_not_service_then_empty_is_rental(self):
        if self.type != 'service':
            self.is_rental = False

    @api.onchange('is_rental')
    def _onchange_is_rental_set_days_as_product_uom(self):
        if self.is_rental:
            uom_day = self.env.ref('product.product_uom_day')
            self.uom_id = uom_day
            self.uom_po_id = uom_day


class ProductWithIsRental(models.Model):

    _inherit = 'product.product'

    @api.onchange('type')
    def _onchange_type_if_not_service_then_empty_is_rental(self):
        if self.type != 'service':
            self.is_rental = False

    @api.onchange('is_rental')
    def _onchange_is_rental_set_days_as_product_uom(self):
        if self.is_rental:
            uom_day = self.env.ref('product.product_uom_day')
            self.uom_id = uom_day
            self.uom_po_id = uom_day


class ProductTemplateWithRentalProduct(models.Model):

    _inherit = 'product.template'

    rental_product_id = fields.Many2one(
        'product.product', 'Rental Product', ondelete='restrict')
