# © 2023 today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    target_margin_min = fields.Float(
        string="Min. Target Margin",
        related="product_id.categ_id.target_margin_min",
    )
    target_margin_max = fields.Float(
        string="Max. Target Margin",
        related="product_id.categ_id.target_margin_max",
    )
