# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    sale_default_privilege_level_id = fields.Many2one(
        "sale.privilege.level",
        related="company_id.default_privilege_level_id",
        readonly=False,
    )
