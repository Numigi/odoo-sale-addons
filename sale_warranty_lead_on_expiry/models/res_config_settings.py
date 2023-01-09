# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    warranty_delay_between_leads = fields.Integer(string="Delay Between Leads")

    def set_values(self):
        super().set_values()

        company = self.env.user.company_id

        if company.warranty_delay_between_leads != self.warranty_delay_between_leads:
            company.sudo().warranty_delay_between_leads = self.warranty_delay_between_leads

    @api.model
    def get_values(self):
        res = super().get_values()
        company = self.env.user.company_id
        res['warranty_delay_between_leads'] = company.warranty_delay_between_leads
        return res
