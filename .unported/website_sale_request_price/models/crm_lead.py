# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import werkzeug

from odoo import api, models, _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model
    def create_website_sale_request(self, post):
        lead = self._create_wsrp_opportunity(post)
        self._send_wsrp_email(lead, post)

    @api.model
    def _create_wsrp_opportunity(self, post):
        user = self.env.user
        is_public = user._is_public()
        product_id = int(float(post["product_product_id"]))
        product = self.env["product.product"].browse(product_id)
        product_brand = product.product_brand_id and [(4, product.product_brand_id.id)]
        email = is_public and post.get("email") or user.partner_id.email
        phone = is_public and post.get("phone") or user.partner_id.phone
        sale_team_id = self._get_wsrp_sale_team_id()
        lead = self.sudo().create(
            {
                "name": "eCom {}".format(product.display_name),
                "type": "opportunity",
                "partner_id": not is_public and user.partner_id.id,
                "email_from": email,
                "phone": phone,
                "team_id": sale_team_id,
                "description": post.get("additional_information"),
                "contact_name": is_public and post.get("name"),
                "brand_ids": product_brand,
                "lead_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "name": product.name,
                            "product_qty": 1,
                        },
                    )
                ],
            }
        )
        lead.lead_line_ids[0]._onchange_product_id()
        return lead

    @api.model
    def _send_wsrp_email(self, lead, post):
        user = self.env.user
        is_public = user._is_public()
        email = is_public and post.get("email") or user.partner_id.email
        mail_template_id = self._get_wsrp_mail_template_id()
        mail_template = self.env["mail.template"].browse(mail_template_id).sudo()
        email_values = {"email_to": email}
        if not is_public:
            email_values.update({"recipient_ids": [(6, 0, [user.partner_id.id])]})
        mail_template.send_mail(lead.id, email_values=email_values)

    @api.model
    def _get_wsrp_parameter(self):
        icp_env = self.env["ir.config_parameter"].sudo()
        active = icp_env.get_param("website_sale_request_price") == "True"
        if not active:
            raise werkzeug.exceptions.NotFound()
        mail_template_id = int(
            icp_env.get_param("website_sale_request_price_mail_template")
        )
        sale_team_id = int(icp_env.get_param("website_sale_request_price_sales_team"))
        return mail_template_id, sale_team_id

    @api.model
    def _get_wsrp_mail_template_id(self):
        return self._get_wsrp_parameter()[0]

    @api.model
    def _get_wsrp_sale_team_id(self):
        return self._get_wsrp_parameter()[1]
