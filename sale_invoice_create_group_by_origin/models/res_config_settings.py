# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    invoice_grouping = fields.Selection(
        [
            ("on", "By SO number"),
            ("off", "By partner and currency"),
        ],
        default="off",
        required=True,
        config_parameter="sale_invoice_create_group_by_origin.config",
    )
