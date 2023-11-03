# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, api


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    @api.depends('partner_id')
    def _compute_available_carrier(self):
        super()._compute_available_carrier()
        for rec in self:
            shipping = rec.order_id.partner_shipping_id
            rec.available_carrier_ids = rec.available_carrier_ids._origin & (
                shipping.get_available_delivery_carriers()
            )
