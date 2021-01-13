# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _


class DeliveryCarrier(models.Model):

    _inherit = "delivery.carrier"

    enable_fixed_over = fields.Boolean()
    fixed_over = fields.Float()
    fixed_over_amount = fields.Float()

    def rate_shipment(self, order):
        res = super().rate_shipment(order)

        if res and res["success"] and self._should_apply_fixed_over(order):
            res["warning_message"] = _(
                "Info:\n"
                "The shipping is {:.2f} because the order amount exceeds {:.2f}.\n"
                "(The actual shipping cost is: {:.2f})"
            ).format(self.fixed_over_amount, self.fixed_over, res["price"])
            res["price"] = self.fixed_over_amount

        return res

    def _should_apply_fixed_over(self, order):
        if not self.enable_fixed_over:
            return False

        order_amount = order._compute_amount_total_without_delivery()

        if self.free_over and order_amount >= self.amount:
            return False

        return order_amount >= self.fixed_over
