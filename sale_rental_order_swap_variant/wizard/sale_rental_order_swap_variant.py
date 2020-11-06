# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleRentalOrderSwapVariant(models.TransientModel):
    _name = "sale.rental.order.swap.variant"

    active_product_id = fields.Many2one("product.product", readonly=True, required=True)
    product_id = fields.Many2one("product.product", required=True)

    @api.onchange("active_product_id")
    def _onchange_active_product_id(self):
        return {
            "domain": {
                "product_id": [
                    ("product_tmpl_id", "=", self.active_product_id.product_tmpl_id.id),
                    ("id", "!=", self.active_product_id.id),
                ]
            }
        }

    @api.multi
    def change_variant(self):
        self.ensure_one()
        context = self._context
        active_sale_line_id = context.get("active_model") == "sale.order.line" and context.get("active_id")
        if not active_sale_line_id:
            raise ValidationError(_("Cannot find any active sale order line"))
        sale_line = self.env["sale.order.line"].browse(active_sale_line_id)
        sale_line.change_variant(self.product_id)
