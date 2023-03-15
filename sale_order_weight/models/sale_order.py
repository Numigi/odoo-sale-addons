from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    weight_in_kg = fields.Float(
        string="Weight of the order (kg)",
        compute="_compute_weight_in_kg",
        digits=dp.get_precision("Stock Weight"),
        store=True,
    )
    weight_in_lb = fields.Float(
        string="Weight of the order (lb)",
        compute="_compute_weight_in_lb",
        digits=dp.get_precision("Stock Weight"),
        store=True,
    )

    @api.depends(
        "order_line",
        "order_line.product_id",
        "order_line.product_uom_qty",
        "order_line.product_uom",
    )
    def _compute_weight_in_kg(self):
        for record in self:
            order_lines = record.order_line.filtered(lambda l: not l.display_type)
            record.weight_in_kg = order_lines.get_weight_in_kg()

    @api.depends(
        "order_line",
        "order_line.product_id",
        "order_line.product_uom_qty",
        "order_line.product_uom",
    )
    def _compute_weight_in_lb(self):
        for record in self:
            order_lines = record.order_line.filtered(lambda l: not l.display_type)
            record.weight_in_lb = order_lines.get_weight_in_lb()
