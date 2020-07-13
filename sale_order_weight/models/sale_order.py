from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):

    _inherit = "sale.order"

    weight_in_kg = fields.Float(
        string="Weight of the order (kg)",
        digits=dp.get_precision('Stock Weight'),
        readonly=True,
    )
    weight_in_lb = fields.Float(
        string="Weight of the order (lb)",
        digits=dp.get_precision('Stock Weight'),
        readonly=True,
    )

    @api.multi
    def compute_weights(self):
        unit_uom_categ = self.env.ref("uom.product_uom_categ_unit")
        unit_uom = self.env.ref("uom.product_uom_unit")
        kgm_uom = self.env.ref("uom.product_uom_kgm")
        lb_uom = self.env.ref("uom.product_uom_lb")
        so_weight_in_kg = 0
        so_weight_in_lb = 0

        for record in self:
            for sol in record.order_line:
                # When user choose uom with category is not Unit, return 0
                if sol.product_uom.category_id != unit_uom_categ:
                    so_weight_in_kg = 0
                    so_weight_in_lb = 0
                    break
                product = sol.product_id
                qty = sol.product_uom_qty
                if sol.product_uom != unit_uom:
                    qty = sol.product_uom._compute_quantity(qty, unit_uom, rounding_method="UP")

                line_weight_in_kg = product.weight * qty
                if product.specific_weight_uom_id == lb_uom:
                    line_weight_in_lb = product.weight_in_uom * qty
                else:
                    line_weight_in_lb = kgm_uom._compute_quantity(line_weight_in_kg, lb_uom, rounding_method="UP")

                so_weight_in_kg += line_weight_in_kg
                so_weight_in_lb += line_weight_in_lb

            record.write({
                "weight_in_kg": so_weight_in_kg,
                "weight_in_lb": so_weight_in_lb,
            })
