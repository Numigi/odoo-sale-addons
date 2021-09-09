# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import werkzeug

from odoo import _, http, models
from odoo.http import request


class WebsiteSaleRequestPriceController(http.Controller):
    @http.route(
        ["/shop/product/request_price"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def request_price(self, **post):
        render = request.env["ir.ui.view"].render_template(
            "website_sale_request_price.request_price_details", post
        )
        return render

    @http.route(
        ["/shop/product/request_price/confirm"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def request_price_confirm(self, **post):
        request.env["crm.lead"].create_website_sale_request(post)
        return werkzeug.utils.redirect(request.httprequest.referrer)
