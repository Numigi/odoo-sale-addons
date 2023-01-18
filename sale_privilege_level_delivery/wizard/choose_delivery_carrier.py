# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import models, api
_logger = logging.getLogger(__name__)
class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    @api.depends('partner_id')
    def _compute_available_carrier(self):
        super()._compute_available_carrier()
        for rec in self:
            rec.available_carrier_ids = rec.available_carrier_ids._origin & (
                rec.order_id.partner_shipping_id.get_available_delivery_carriers()
            )
