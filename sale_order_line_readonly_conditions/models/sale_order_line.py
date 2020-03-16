# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    handle_widget_invisible = fields.Boolean()
    trash_widget_invisible = fields.Boolean()
    product_readonly = fields.Boolean()
    product_uom_qty_readonly = fields.Boolean()
    product_uom_readonly = fields.Boolean()
