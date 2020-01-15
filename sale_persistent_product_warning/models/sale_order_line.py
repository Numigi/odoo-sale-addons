# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    product_warning = fields.Text(
        "Product Warning Message",
        related='product_id.sale_line_warn_msg',
    )
