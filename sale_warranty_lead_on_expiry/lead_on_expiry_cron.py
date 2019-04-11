# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo import api, fields, models

DEFAULT_DELAY_BETWEEN_LEADS = 21


class WarrantyType(models.Model):

    _inherit = 'sale.warranty.type'

    automated_action = fields.Boolean(
        'Automated Warranty End Action',
    )

    sales_team_id = fields.Many2one(
        'sales.team', 'Sales Team', ondelete='restrict'
    )

    automated_action_delay = fields.Integer('Days To Trigger Action')


class Company(models.Model):

    _inherit = 'res.company'

    warranty_delay_between_leads = fields.Integer(
        string="Warranty Delay Between Leads", default=DEFAULT_DELAY_BETWEEN_LEADS)


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


class CrmLead(models.Model):

    _inherit = 'crm.lead'

    generated_from_warranty = fields.Boolean()


class Warranty(models.Model):

    _inherit = 'sale.warranty'

    lead_id = fields.Many2one('crm.lead', 'Warranty End Action', ondelete='restrict')

    def _is_days_to_trigger_exceeded(self):
        """Check whether the days to trigger the actions have been exceeded.

        If the warranty has an extension, the extension date is used.
        Extensions are enabled by the module `sale_warranty_extension`,
        which is not a dependency for the current module.

        :rtype: Bool
        """
        today = datetime.now().date()
        extension_expiry_date = getattr(self, 'extension_expiry_date', False)
        expiry_date = extension_expiry_date or self.expiry_date
        delay_in_days = self.type_id.automated_action_delay or 0
        return expiry_date + timedelta(delay_in_days) <= today

    def _get_delay_between_leads(self):
        return (
            self.env.user.company_id.warranty_delay_between_leads or
            DEFAULT_DELAY_BETWEEN_LEADS
        )

    def _find_last_generated_lead_for_partner(self):
        return self.env['crm.lead'].search([
            ('generated_from_warranty', '=', True),
            ('partner_id', '=', self.partner_id.id),
        ], limit=1, order='id desc')

    def _is_delay_between_leads_exceeded(self):
        today = datetime.now().date()
        delay_in_days = self._get_delay_between_leads()
        previous_lead = self._find_last_generated_lead_for_partner()
        return previous_lead.create_date.date() + timedelta(delay_in_days) <= today

    def _format_lead_name(self):
        return "End Of Warranty {}".format(self.reference)

    def _generate_new_lead(self):
        new_lead = self.env['crm.lead'].create({
            'name': self._format_lead_name(),
            'partner_id': self.partner_id.id,
            'team_id': self.type_id.sales_team_id.id,
        })

    def lead_on_expiry_cron(self):
        expired_warranties_to_process = self.search([
            ('type_id.automated_action', '=', True),
            ('lead_id', '=', False),
            ('state', '=', 'expired'),
        ])

        for warranty in expired_warranties_to_process:
            days_to_trigger_exceeded = self._is_days_to_trigger_exceeded()
            delay_between_leads_exceeded = self._is_delay_between_leads_exceeded()

            if days_to_trigger_exceeded and delay_between_leads_exceeded:
                warranty._generate_new_lead()

            if days_to_trigger_exceeded and not delay_between_leads_exceeded:
                warranty._bind_warranty_to_last_generated_lead()

        return True
