# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from decimal import Decimal, ROUND_HALF_UP
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

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


_logger = logging.getLogger(__name__)


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

    standard_price = fields.Float(track_visibility='onchange')
    lst_price = fields.Float(track_visibility='onchange')

    price_type = fields.Selection(
        [
            ('fixed', 'Fixed'),
            ('dynamic', 'Dynamic'),
        ],
        default='fixed',
        track_visibility='onchange',
    )

    margin = fields.Float(track_visibility='onchange')
    margin_amount = fields.Float(
        track_visibility='onchange',
        digits=dp.get_precision('Product Price'),
    )
    price_rounding = fields.Selection([
        (a, a) for a in ROUNDING_AMOUNTS
    ], string="Rounding", track_visibility='onchange')
    price_surcharge = fields.Float(
        track_visibility='onchange',
        digits=dp.get_precision('Product Price'),
    )

    def _compute_margin_amount(self):
        margin_ratio = 1 - (self.margin or 0)
        if margin_ratio:
            cost = self.standard_price or 0
            cost_plus_margin = cost / margin_ratio
            return cost_plus_margin - cost
        else:
            return 0

    @api.onchange('standard_price', 'margin')
    def _onchange_set_margin_amount(self):
        self.margin_amount = self._compute_margin_amount()

    def _compute_sale_price_from_cost(self):
        cost = self.standard_price or 0
        margin = self._compute_margin_amount()
        price = cost + margin

        rounding = self.price_rounding
        if rounding:
            price = round_price(price, rounding)

        surcharge = self.price_surcharge or 0
        return price + surcharge

    @api.onchange('margin_amount', 'price_rounding', 'price_surcharge', 'price_type')
    def _onchange_compute_dynamic_price(self):
        if self.price_type == 'dynamic':
            self.lst_price = self._compute_sale_price_from_cost()

    def update_sale_price_from_cost(self):
        """Compute the sale price based on the product cost.

        The computation is only done on products with dynamic price.
        """
        products_with_dynamic_price = self.filtered(lambda p: p.price_type == 'dynamic')
        for product in products_with_dynamic_price:
            product.write({
                'margin_amount': product._compute_margin_amount(),
                'lst_price': product._compute_sale_price_from_cost(),
            })

    def _get_products_with_dynamic_price_to_update(self):
        """Get all products to update with the dynamic price cron.

        If the margin of a product and its sale price are unchanged,
        do not update the sale price. This makes the cron much faster because
        the number of insert/update queries to the database is reduced.

        :rtype: product.product recordset
        """
        products_with_dynamic_price = self.env['product.product'].search([
            ('price_type', '=', 'dynamic'),
        ])
        return products_with_dynamic_price.filtered(
            lambda p: (
                p.margin_amount != p._compute_margin_amount() or
                p.lst_price != p._compute_sale_price_from_cost()
            )
        )

    def sale_price_update_cron(self):
        """Cron to update dynamic sale prices on all products."""
        products = self._get_products_with_dynamic_price_to_update()
        _logger.info(
            "Updating the dynamic sale prices of {} products."
            .format(len(products))
        )
        for prod in products:
            prod.update_sale_price_from_cost()


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    standard_price = fields.Float(track_visibility='onchange')
    list_price = fields.Float(track_visibility='onchange')

    price_type = fields.Selection(
        related='product_variant_ids.price_type',
        readonly=False,
        store=True,
    )
    margin = fields.Float(
        related='product_variant_ids.margin',
        readonly=False,
        store=True,
    )
    margin_amount = fields.Float(
        related='product_variant_ids.margin_amount',
        readonly=False,
        store=True,
    )
    price_rounding = fields.Selection(
        related='product_variant_ids.price_rounding',
        readonly=False,
        store=True,
    )
    price_surcharge = fields.Float(
        related='product_variant_ids.price_surcharge',
        readonly=False,
        store=True,
    )

    @api.model
    def create(self, vals):
        template = super().create(vals)

        fields_to_propagate = (
            'price_type',
            'margin',
            'margin_amount',
            'price_rounding',
            'price_surcharge',
            'list_price',
        )

        vals_to_propagate = {k: v for k, v in vals.items() if k in fields_to_propagate}

        for variant in template.product_variant_ids:
            # Only write values that are different from the variant's default value.
            changed_values_to_propagate = {
                k: v for k, v in vals_to_propagate.items()
                if (v or variant[k]) and v != variant[k]
            }
            variant.write(changed_values_to_propagate)

        return template

    _compute_margin_amount = Product._compute_margin_amount
    _compute_sale_price_from_cost = Product._compute_sale_price_from_cost

    @api.onchange('standard_price', 'margin')
    def _onchange_set_margin_amount(self):
        self.margin_amount = self._compute_margin_amount()

    @api.onchange('margin_amount', 'price_rounding', 'price_surcharge', 'price_type')
    def _onchange_compute_dynamic_price(self):
        if self.price_type == 'dynamic':
            self.list_price = self._compute_sale_price_from_cost()
