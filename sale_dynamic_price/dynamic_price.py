# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from decimal import Decimal, ROUND_HALF_UP
from odoo import api, fields, models

ROUNDING_AMOUNTS = [
    '0.01',
    '0.05',
    '0.1',
    '0.5',
    '1',
    '5',
    '10',
    '50',
    '100',
    '500',
    '1000',
]


def round_price(price: float, rounding: str) -> str:
    """Round the given price using a rounding amount.

    The rounding amount can be any of the values of ROUNDING_AMOUNTS.

    :param price: the price to round
    :param rounding: the rounding amount to apply
    :return: the rounded price
    """
    factor = (Decimal(price) / Decimal(rounding)).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
    result_decimal = factor * Decimal(rounding)
    return float(result_decimal)


class Product(models.Model):

    _inherit = 'product.product'

    price_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('dynamic', 'Dynamic'),
    ], default='fixed')

    margin = fields.Float()
    margin_amount = fields.Float(compute='_compute_margin_amount')
    price_rounding = fields.Selection([
        (a, a) for a in ROUNDING_AMOUNTS
    ])
    price_surcharge = fields.Float()

    @api.depends('standard_price', 'margin')
    def _compute_margin_amount(self):
        for product in self:
            margin_ratio = 1 - (product.margin or 0)
            if margin_ratio:
                cost = product.standard_price or 0
                cost_plus_margin = cost / margin_ratio
                product.margin_amount = cost_plus_margin - cost

    def compute_sale_price_from_cost(self):
        """Compute the sale price based on the product cost.

        The computation is only done on products with dynamic price.
        """
        products_with_dynamic_price = self.filtered(lambda p: p.price_type == 'dynamic')
        for product in products_with_dynamic_price:
            cost = product.standard_price or 0
            price = cost + product.margin_amount
            surcharge = product.price_surcharge or 0
            product.list_price = round_price(price, product.price_rounding) + surcharge
