# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    inventory_availability = fields.Selection(
        selection_add=[
            (
                "threshold_warning",
                "Indicate if the inventory is below a threshold and allow sales if not enough stock",
            ),
        ]
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
        info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )

        if "virtual_available" in info:
            product = self.env["product.product"].sudo().browse(info["product_id"])
            product._set_enhanced_availability_info(info, add_qty)

        return info
