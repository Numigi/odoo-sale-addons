# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from ..rounding import ROUNDING_AMOUNTS, round_price


_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = "product.product"

    standard_price = fields.Float(tracking=True)
    lst_price = fields.Float(tracking=True)

    price_type = fields.Selection(
        [
            ("fixed", "Fixed"),
            ("dynamic", "Dynamic"),
        ],
        default="fixed",
        tracking=True,
    )

    margin = fields.Float(tracking=True)
    margin_amount = fields.Float(
        tracking=True,
        digits=dp.get_precision("Product Price"),
    )
    price_rounding = fields.Selection(
        [(a, a) for a in ROUNDING_AMOUNTS], string="Rounding", tracking=True
    )
    price_surcharge = fields.Float(
        tracking=True,
        digits=dp.get_precision("Product Price"),
    )

    def _compute_margin_amount(self):
        margin_ratio = 1 - (self.margin or 0)
        if margin_ratio:
            cost = self.standard_price or 0
            cost_plus_margin = cost / margin_ratio
            return cost_plus_margin - cost
        else:
            return 0

    @api.onchange("standard_price", "margin")
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

    @api.onchange("margin_amount", "price_rounding", "price_surcharge", "price_type")
    def _onchange_compute_dynamic_price(self):
        if self.price_type == "dynamic":
            self.lst_price = self._compute_sale_price_from_cost()

    def sale_price_update_cron(self):
        """Cron to update dynamic sale prices on all products."""
        products = self._get_products_with_dynamic_price_to_update()
        _logger.info(
            "Updating the dynamic sale prices of {} products.".format(len(products))
        )
        for prod in products:
            prod.update_sale_price_from_cost()

    def update_sale_price_from_cost(self):
        """Compute the sale price based on the product cost.

        The computation is only done on products with dynamic price.
        """
        products_with_dynamic_price = self.filtered(lambda p: p.price_type == "dynamic")
        for product in products_with_dynamic_price:
            product.write(
                {
                    "margin_amount": product._compute_margin_amount(),
                    "lst_price": product._compute_sale_price_from_cost(),
                }
            )

    def _get_products_with_dynamic_price_to_update(self):
        """Get all products to update with the dynamic price cron.

        If the margin of a product and its sale price are unchanged,
        do not update the sale price. This makes the cron much faster because
        the number of insert/update queries to the database is reduced.

        :rtype: product.product recordset
        """
        products_with_dynamic_price = self.env["product.product"].search(
            [
                ("price_type", "=", "dynamic"),
            ]
        )
        return products_with_dynamic_price.filtered(
            lambda p: (
                p.margin_amount != p._compute_margin_amount()
                or p.lst_price != p._compute_sale_price_from_cost()
            )
        )
