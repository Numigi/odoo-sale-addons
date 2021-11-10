# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    block_website_sales_based_on = fields.Selection(
        [
            (
                "sale_availability",
                "Quantity Available For Sales",
            ),
            (
                "replenishment_availability",
                "Quantity Available Including Next Replenishment",
            ),
        ],
        default="replenishment_availability",
    )
    inventory_availability = fields.Selection(
        selection_add=[
            (
                "threshold_warning",
                "Indicate if the inventory is below a threshold and allow sales if not enough stock",
            ),
        ]
    )
    replenishment_delay = fields.Integer(
        related="product_variant_ids.replenishment_delay",
        readonly=False,
    )
    replenishment_availability = fields.Float(
        related="product_variant_ids.replenishment_availability",
        readonly=False,
    )
    sale_availability = fields.Float(
        related="product_variant_ids.sale_availability",
        readonly=False,
    )

    @api.multi
    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        pricelist=False,
        parent_combination=False,
        only_template=False,
    ):
        get_quantity = self._context.get("website_sale_stock_get_quantity")
        self = self.with_context(website_sale_stock_get_quantity=False)

        info = super(ProductTemplate, self)._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )

        product_id = info["product_id"]
        if get_quantity and product_id:
            product = self.env["product.product"].sudo().browse(product_id)
            info.update(product._get_enhanced_availability_info(add_qty))

        return info
