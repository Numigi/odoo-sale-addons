# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    # def _compute_available_carrier(self):
    #     super()._compute_available_carrier()
    #     for order in self:
    #         order.available_carrier_ids &= (
    #             order.partner_shipping_id.get_available_delivery_carriers()
    #         )
