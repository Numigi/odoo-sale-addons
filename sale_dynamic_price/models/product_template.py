# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from .product_product import Product


class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_price = fields.Float(tracking=True)
    list_price = fields.Float(tracking=True)

    price_type = fields.Selection(
        related="product_variant_ids.price_type",
        readonly=False,
        store=True,
        default="fixed",
    )
    margin = fields.Float(
        related="product_variant_ids.margin",
        readonly=False,
        store=True,
    )
    margin_amount = fields.Float(
        related="product_variant_ids.margin_amount",
        readonly=False,
        store=True,
    )
    price_rounding = fields.Selection(
        related="product_variant_ids.price_rounding",
        readonly=False,
        store=True,
    )
    price_surcharge = fields.Float(
        related="product_variant_ids.price_surcharge",
        readonly=False,
        store=True,
    )

    @api.model
    def create(self, vals):
        template = super().create(vals)

        fields_to_propagate = (
            "price_type",
            "margin",
            "margin_amount",
            "price_rounding",
            "price_surcharge",
            "list_price",
        )

        vals_to_propagate = {k: v for k, v in vals.items() if k in fields_to_propagate}

        for variant in template.product_variant_ids:
            # Only write values that are different from the variant's default value.
            changed_values_to_propagate = {
                k: v
                for k, v in vals_to_propagate.items()
                if (v or variant[k]) and v != variant[k]
            }
            variant.write(changed_values_to_propagate)

        return template

    _compute_margin_amount = Product._compute_margin_amount
    _compute_sale_price_from_cost = Product._compute_sale_price_from_cost

    @api.onchange("standard_price", "margin")
    def _onchange_set_margin_amount(self):
        self.margin_amount = self._compute_margin_amount()

    @api.onchange("margin_amount", "price_rounding", "price_surcharge", "price_type")
    def _onchange_compute_dynamic_price(self):
        if self.price_type == "dynamic":
            self.list_price = self._compute_sale_price_from_cost()
