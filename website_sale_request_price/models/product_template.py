# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def is_request_price_required(self):
        self.ensure_one()
        website_sale_request_price_vals = self.get_website_sale_request_price_vals()
        if website_sale_request_price_vals["active"]:
            if self.list_price >= website_sale_request_price_vals["threshold"]:
                return True
        return False

    def get_website_sale_request_price_vals(self):
        icp_env = self.env['ir.config_parameter'].sudo()
        active = icp_env.get_param("website_sale_request_price") == "True"
        threshold = float(icp_env.get_param("website_sale_request_price_threshold"))
        return {
            "active": active,
            "threshold": threshold,
        }
