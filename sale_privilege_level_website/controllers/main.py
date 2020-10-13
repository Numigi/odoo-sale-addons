# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery


class WebsiteSaleWithPrivilegeLevels(WebsiteSaleDelivery):
    def _get_shop_payment_values(self, order, **kwargs):
        order = order.with_context(sale_privilege_level_partner_id=order.partner_id.id)
        return super()._get_shop_payment_values(order, **kwargs)
