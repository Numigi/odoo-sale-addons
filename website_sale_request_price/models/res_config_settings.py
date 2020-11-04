# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_sale_request_price = fields.Boolean(
        config_parameter="website_sale_request_price"
    )
    website_sale_request_price_threshold = fields.Float(
        config_parameter="website_sale_request_price_threshold"
    )
    website_sale_request_price_mail_template = fields.Many2one(
        "mail.template",
        config_parameter="website_sale_request_price_mail_template"
    )
    website_sale_request_price_sales_team = fields.Many2one(
        "crm.team",
        config_parameter="website_sale_request_price_sales_team"
    )

    @api.multi
    def set_values(self):
        if self.website_sale_request_price_mail_template.model_id.model != "crm.lead":
            raise UserError(_("Website Sale Request Price's Mail Template must be linked to Lead/Opportunity model"))
        return super().set_values()
