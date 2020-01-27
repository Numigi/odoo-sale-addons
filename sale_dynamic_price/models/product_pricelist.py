# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models
from odoo.addons.product.models.product import ProductProduct as Product
from ..rounding import round_price


class PricelistWithDynamicPrice(models.Model):

    _inherit = 'product.pricelist'

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """Apply the rounding and surcharge defined on dynamic products."""
        result = super()._compute_price_rule(
            products_qty_partner, date=date, uom_id=uom_id)

        for product_id, (price, suitable_rule) in result.items():
            product = self.env['product.product'].browse(product_id)

            is_price_dynamic = product.price_type == 'dynamic'
            is_not_public_price = price != product.list_price

            if is_price_dynamic and is_not_public_price:
                new_price = _apply_rounding_and_surcharge_to_price(product, price)
                result[product_id] = (new_price, suitable_rule)

        return result


def _apply_rounding_and_surcharge_to_price(product: 'product.product', price: float) -> float:
    """Apply the rounding and surcharge of the product to the given price."""
    rounding = product.price_rounding
    rounded_price = round_price(price, rounding)
    surcharge = (product.price_surcharge or 0)
    return rounded_price + surcharge
