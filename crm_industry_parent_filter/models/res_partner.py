# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.onchange("industry_id")
    def _onchange_industry_id__update_secondary_industries(self):
        self.secondary_industry_ids = self.secondary_industry_ids.filtered(
            lambda s: s.parent_id in self.industry_id
        )
