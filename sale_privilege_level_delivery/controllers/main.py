# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.http import request
from odoo.tools import frozendict
from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery


class WebsiteSaleWithPrivilegeLevels(WebsiteSaleDelivery):
    def _get_shop_payment_values(self, order, **kwargs):
        partner = order.partner_id
        available_carriers = partner.get_available_delivery_carriers()
        order = order.with_context(filter_delivery_carrier_ids=available_carriers.ids)
        return super()._get_shop_payment_values(order, **kwargs)
