# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_warning = fields.Text(
        "Product Warning Message",
        compute="_compute_product_warning",
    )

    def _compute_product_warning(self):
        product_warning = False
        for line in self:
            if line.product_id.sale_line_warn != "no-message":
                product_warning = line.product_id.sale_line_warn_msg
            line.product_warning = product_warning
