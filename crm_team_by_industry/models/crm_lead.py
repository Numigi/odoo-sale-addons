# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.onchange("industry_id")
    def _onchange_industry_id(self):
        if self.industry_id and self.industry_id.crm_team_id:
            self.team_id = self.industry_id.crm_team_id
