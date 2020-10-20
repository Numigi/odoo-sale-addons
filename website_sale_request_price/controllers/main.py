# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import werkzeug

from odoo import _, http, models
from odoo.http import request


class WebsiteSaleRequestPriceController(http.Controller):

    @http.route(
        ['/shop/product/<model("product.template"):prod_tmpl>/request_price'],
        type='json', auth="public", methods=['POST'], website=True
    )
    def request_price(self, prod_tmpl, **post):
        print("-------request_price", post)
        product_product = request.env["product.product"].browse(post["product_id"])
        render = request.env['ir.ui.view'].render_template(
            "website_sale_request_price.request_price_details",
            {"product": product_product or prod_tmpl}
        )
        return render

    @http.route(
        ['/shop/product/<model("product.template"):prod_tmpl>/request_price/confirm'],
        type='http', auth="public", methods=['POST'], website=True
    )
    def request_price_confirm(self, prod_tmpl, **post):
        icp_env = request.env["ir.config_parameter"].sudo()
        active = icp_env.get_param("website_sale_request_price") == "True"
        mail_template_id = int(icp_env.get_param("website_sale_request_price_mail_template"))
        sale_team_id = int(icp_env.get_param("website_sale_request_price_sales_team"))
        if not active:
            return request.not_found()
        mail_template = request.env["mail.template"].browse(mail_template_id)
        user = request.env.user
        is_public = user._is_public()
        product = post["product"]

        lead = request.env["crm.lead"] .create(
            {
                "name": "Shop: " + product.display_name,  # TODO: handle variant
                "email_from": is_public and post["email"] or user.email,
                "phone": is_public and post.get("phone") or user.partner_id.phone,
                "team_id": sale_team_id,
                "description": post.get("additional_information"),
                "contact_name": is_public and post["name"] or user.name,
                "brand_ids":
                    product.product_brand_id and [(4, product.product_brand_id.id)],
                "lead_line_ids": [(0, 0, {
                    "product_id": product.id,
                    "name": product.name,
                })]
            }
        )
        lead.lead_line_ids[0]._onchange_product_id()
        mail_template.send_mail(lead.id)
        return werkzeug.utils.redirect('/shop')
