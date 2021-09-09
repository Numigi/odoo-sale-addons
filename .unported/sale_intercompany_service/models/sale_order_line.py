# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.constrains("product_id")
    def _check_interco_products_shared_between_companies(self):
        lines = self.filtered("order_id.is_interco_service").filtered(
            "product_id.company_id"
        )
        if lines:
            raise ValidationError(
                _(
                    "The following products are not shared between companies: {products}."
                    "\n\n"
                    "A product must be shared between companies in order "
                    "to be sold in an intercompany service order."
                ).format(products=", ".join(lines.mapped("product_id.display_name")))
            )
