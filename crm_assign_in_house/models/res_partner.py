# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    in_house = fields.Boolean("In-house")

    @api.model
    def _commercial_fields(self):
        res = super()._commercial_fields()
        res.append("in_house")
        res.append("user_id")
        return res
