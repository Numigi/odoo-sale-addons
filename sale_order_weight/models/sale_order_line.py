from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.order_id.compute_weights()
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if (
            vals.get("product_id")
            or vals.get("product_uom_qty")
            or vals.get("product_uom")
        ):
            self.mapped("order_id").compute_weights()
        return res
