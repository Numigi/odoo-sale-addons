# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class Product(models.Model):
    """Store the sale price on the product_product table.

    This allows 2 variants of the same product template
    to have different sale prices.
    """

    _inherit = 'product.product'

    list_price = fields.Float(
        'Product Price',
        digits=dp.get_precision('Product Price')
    )


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    list_price = fields.Float(
        related='product_variant_ids.list_price',
        readonly=False,
        store=True,
    )
