# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_request_price_required = fields.Boolean(
        compute="_compute_is_request_price_required"
    )

    def _compute_is_request_price_required(self):
        vals = self.get_website_sale_request_price_vals()
        active = vals["active"]
        threshold = vals["threshold"]

        for product in self:
            product.is_request_price_required = (
                active and product.list_price >= threshold
            )

    def get_website_sale_request_price_vals(self):
        icp_env = self.env["ir.config_parameter"].sudo()
        active = icp_env.get_param("website_sale_request_price") == "True"
        threshold = float(icp_env.get_param("website_sale_request_price_threshold"))
        return {"active": active, "threshold": threshold}
