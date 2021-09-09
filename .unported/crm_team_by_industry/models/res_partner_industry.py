# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerIndustry(models.Model):
    _inherit = "res.partner.industry"

    crm_team_id = fields.Many2one(comodel_name="crm.team", string="Sales Team")
