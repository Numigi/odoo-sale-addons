# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

ALMOST_OUT_OF_STOCK_PARAM = "sale_order_available_qty_popover.almost_out_of_stock_qty"
GREEN = "#246b03"
YELLOW = "#dddb01"
RED = "#ee1010"


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    product_type = fields.Selection(related="product_id.type")
    product_default_uom = fields.Many2one(related="product_id.uom_id")

    available_qty_for_popover = fields.Float(
        compute="_compute_available_qty_for_popover"
    )

    available_qty_popover_color = fields.Char(
        compute="_compute_available_qty_popover_color"
    )

    @api.depends("product_id")
    def _compute_available_qty_for_popover(self):
        for line in self:
            line.available_qty_for_popover = line._get_available_qty_for_popover()

    def _get_available_qty_for_popover(self):
        return self.product_id.with_context(company_owned=True).qty_available

    @api.depends("product_id")
    def _compute_available_qty_popover_color(self):
        almost_out_of_stock = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(ALMOST_OUT_OF_STOCK_PARAM, 2)
        )
        for line in self:
            if line.available_qty_for_popover > almost_out_of_stock:
                line.available_qty_popover_color = GREEN
            elif line.available_qty_for_popover:
                line.available_qty_popover_color = YELLOW
            else:
                line.available_qty_popover_color = RED
