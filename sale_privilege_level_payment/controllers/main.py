# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.http import request
from odoo.tools import frozendict
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleWithPrivilegeLevels(WebsiteSale):
    def _get_shop_payment_values(self, order, **kwargs):
        partner = order.partner_id
        available_acquirers = partner.get_available_payment_acquirers()

        new_context = dict(
            request.env.context, filter_payment_acquirer_ids=available_acquirers.ids
        )
        request.env.context = frozendict(new_context)

        return super()._get_shop_payment_values(order, **kwargs)
