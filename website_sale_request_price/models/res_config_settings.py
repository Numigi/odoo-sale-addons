# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_sale_request_price = fields.Boolean(
        config_parameter="website_sale_request_price"
    )
    website_sale_request_price_threshold = fields.Float(
        config_parameter="website_sale_request_price_threshold"
    )
    website_sale_request_price_message = fields.Text(
        related="company_id.website_sale_request_price_message",
        readonly=False,
    )
    website_sale_request_price_mail_template = fields.Many2one(
        "mail.template",
        config_parameter="website_sale_request_price_mail_template",
        domain=[("model_id.model", "=", "crm.lead")],
    )
    website_sale_request_price_sales_team = fields.Many2one(
        "crm.team", config_parameter="website_sale_request_price_sales_team"
    )
