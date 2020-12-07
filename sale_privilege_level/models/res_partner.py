# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.model
    def _default_privilege_level(self):
        return self.env.user.company_id.default_privilege_level_id

    privilege_level_id = fields.Many2one(
        "sale.privilege.level", ondelete="restrict", default=_default_privilege_level
    )
