# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    def copy(self, default=None):
        user = super().copy(default)
        user.partner_id.privilege_level_id = self.env[
            "res.partner"
        ]._default_privilege_level()
        return user
