# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models


class SaleRentalOrderSwapVariant(models.TransientModel):
    _name = "sale.rental.order.swap.variant"
    _description = "Sale Rental Order Swap Variant"

    sale_line_id = fields.Many2one("sale.order.line")
    product_id = fields.Many2one("product.product", required=True)
    quantity = fields.Float(required=True)

    @api.onchange("sale_line_id")
    def _onchange_sale_line_id(self):
        self.product_id = self.sale_line_id.product_id
        self.quantity = self.sale_line_id.product_uom_qty
        return {
            "domain": {
                "product_id": self._get_product_domain(),
            }
        }

    def _get_product_domain(self):
        active_variant = self.sale_line_id.product_id
        if self.sale_line_id.allow_change_product:
            return [
                ("id", "!=", active_variant.id),
            ]
        else:
            return [
                ("product_tmpl_id", "=", active_variant.product_tmpl_id.id),
                ("id", "!=", active_variant.id),
            ]

    def change_variant(self):
        line = self.sale_line_id
        line.change_variant(self.product_id, self.quantity)
