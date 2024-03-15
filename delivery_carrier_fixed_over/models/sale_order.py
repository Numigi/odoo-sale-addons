# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _compute_amount_total_without_delivery(self):
        self.ensure_one()
        delivery_cost = sum(
            [line.price_subtotal for line in self.order_line if line.is_delivery]
        )
        return self.amount_untaxed - delivery_cost
