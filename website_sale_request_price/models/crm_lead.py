# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model
    def create_website_sale_request(self, post):
        icp_env = self.env["ir.config_parameter"].sudo()
        active = icp_env.get_param("website_sale_request_price") == "True"
        if not active:
            return self.not_found()
        mail_template_id = int(icp_env.get_param("website_sale_request_price_mail_template"))
        sale_team_id = int(icp_env.get_param("website_sale_request_price_sales_team"))
        mail_template = self.env["mail.template"].browse(mail_template_id).sudo()
        user = self.env.user
        is_public = user._is_public()
        product = self.env["product.product"].browse(int(post["product_product_id"]))
        product_brand = product.product_brand_id and [(4, product.product_brand_id.id)]
        email = is_public and post.get("email") or user.partner_id.email
        phone = is_public and post.get("phone") or user.partner_id.phone

        lead = self.sudo().create(
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
                    "product_qty": 1,
                })]
            }
        )
        lead.lead_line_ids[0]._onchange_product_id()
        email_values = {"email_to": email}
        if not is_public:
            email_values.update({"recipient_ids": [(6, 0, [user.partner_id.id])]})
        mail_template.send_mail(lead.id, email_values=email_values)
