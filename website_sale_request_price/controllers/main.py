# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import werkzeug

from odoo import _, http, models
from odoo.http import request


class WebsiteSaleRequestPriceController(http.Controller):

    @http.route(
        ['/shop/product/request_price'],
        type='json', auth="public", methods=['POST'], website=True
    )
    def request_price(self, **post):
        render = request.env['ir.ui.view'].render_template(
            "website_sale_request_price.request_price_details", post
        )
        return render

    @http.route(
        ['/shop/product/request_price/confirm'],
        type='http', auth="public", methods=['POST'], website=True
    )
    def request_price_confirm(self, **post):
        icp_env = request.env["ir.config_parameter"].sudo()
        crm_lead_env = request.env["crm.lead"].sudo()
        active = icp_env.get_param("website_sale_request_price") == "True"
        mail_template_id = int(icp_env.get_param("website_sale_request_price_mail_template"))
        sale_team_id = int(icp_env.get_param("website_sale_request_price_sales_team"))
        if not active:
            return request.not_found()
        mail_template = request.env["mail.template"].browse(mail_template_id).sudo()
        user = request.env.user
        is_public = user._is_public()
        product = request.env["product.product"].browse(int(post["product_product_id"]))
        product_brand = product.product_brand_id and [(4, product.product_brand_id.id)]
        email = is_public and post.get("email") or user.partner_id.email
        phone = is_public and post.get("phone") or user.partner_id.phone

        lead = crm_lead_env.create(
            {
                "name": "Shop: " + product.display_name,
                "type": "opportunity",
                "partner_id": not is_public and user.partner_id.id,
                "email_from": email,
                "phone": phone,
                "team_id": sale_team_id,
                "description": post.get("additional_information"),
                "contact_name": is_public and post.get("name"),
                "brand_ids": product_brand,
                "lead_line_ids": [(0, 0, {
                    "product_id": product.id,
                    "name": product.name,
                    "product_qty": float(post["product_qty"])
                })]
            }
        )
        lead.lead_line_ids[0]._onchange_product_id()
        email_values = {"email_to": email}
        if not is_public:
            email_values.update({"recipient_ids": [(6, 0, [user.partner_id.id])]})
        mail_template.send_mail(lead.id, email_values=email_values)
        return werkzeug.utils.redirect('/shop')
