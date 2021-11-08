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
            info["show_product_availability"] = self._get_show_product_availability()
            info["always_show_available_qty"] = self._get_always_show_available_qty()
            info["enough_in_stock"] = self._get_enough_in_stock(info, add_qty)

        return info

    def _get_show_product_availability(self):
        return self.inventory_availability not in ("never", "custom")

    def _get_always_show_available_qty(self):
        return self.inventory_availability == "always"

    def _get_enough_in_stock(self, info, add_qty):
        return info["virtual_available"] >= add_qty
