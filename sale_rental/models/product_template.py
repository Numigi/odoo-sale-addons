# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplateWithRentalOK(models.Model):

    _inherit = 'product.template'

    rental_ok = fields.Boolean('Can be Rented')


class ProductTemplateWithRentalProduct(models.Model):

    _inherit = 'product.template'

    rental_product_id = fields.Many2one(
        'product.product', 'Rental Product', ondelete='restrict',
        domain="[('type', '=', 'service')]")
