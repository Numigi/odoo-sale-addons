# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.http import request, route
from odoo.tools import frozendict
from odoo.addons.sale.controllers.portal import CustomerPortal


class CustomerPortalWithPrivilegeLevels(CustomerPortal):
    @route(["/my/orders/<int:order_id>"], type="http", auth="public", website=True)
    def portal_order_page(
        self,
        order_id,
        report_type=None,
        access_token=None,
        message=False,
        download=False,
        **kw
    ):
        env = request.env
        order = env["sale.order"].sudo().browse(order_id)
        new_context = {"sale_privilege_level_partner_id": order.partner_id.id}
        env.context = frozendict(request.env.context, **new_context)
        return super().portal_order_page(
            order_id, report_type, access_token, message, download, **kw
        )
