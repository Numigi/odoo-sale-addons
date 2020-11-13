from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.multi
    def get_weight_in_kg(self):
        weight_in_kg = 0
        for record in self:
            qty = record.get_qty_in_product_product_uom()
            weight_in_kg += record.product_id.weight * qty
        return weight_in_kg

    @api.multi
    def get_weight_in_lb(self):
        kgm_uom = self.env.ref("uom.product_uom_kgm")
        lb_uom = self.env.ref("uom.product_uom_lb")
        weight_in_lb = 0
        for record in self:
            product = record.product_id
            if product.specific_weight_uom_id == lb_uom:
                qty = record.get_qty_in_product_product_uom()
                weight_in_lb += product.weight_in_uom * qty
            else:
                weight_in_kg = record.get_weight_in_kg()
                weight_in_lb += kgm_uom._compute_quantity(
                    weight_in_kg, lb_uom, rounding_method="UP"
                )
        return weight_in_lb

    @api.multi
    def get_qty_in_product_product_uom(self):
        self.ensure_one()
        qty = self.product_uom_qty
        product_product_uom = self.product_id.uom_id
        if self.product_uom != product_product_uom:
            qty = self.product_uom._compute_quantity(
                qty, product_product_uom, rounding_method="UP"
            )
        return qty
