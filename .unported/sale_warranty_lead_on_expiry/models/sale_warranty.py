# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from .common import DEFAULT_DELAY_BETWEEN_LEADS


class Warranty(models.Model):

    _inherit = 'sale.warranty'

    lead_id = fields.Many2one(
        'crm.lead', 'Warranty End Action', ondelete='restrict',
        copy=False)

    def lead_on_expiry_cron(self):
        """Generate leads from active warranties."""
        expired_warranties_to_process = self.search([
            ('type_id.automated_action', '=', True),
            ('lead_id', '=', False),
            ('state', '=', 'active'),
        ])

        for warranty in expired_warranties_to_process:
            days_to_trigger_reached = warranty._is_days_to_trigger_reached()
            delay_between_leads_reached = warranty._is_delay_between_leads_reached()

            if days_to_trigger_reached and delay_between_leads_reached:
                warranty._generate_new_lead()

            if days_to_trigger_reached and not delay_between_leads_reached:
                warranty._bind_warranty_to_last_generated_lead()

        return True

    def _is_days_to_trigger_reached(self):
        """Check whether the days to trigger the actions have been reached.

        If the warranty has an extension, the extension date is used.
        Extensions are enabled by the module `sale_warranty_extension`,
        which is not a dependency for the current module.

        :rtype: bool
        """
        today = datetime.now().date()
        extension_expiry_date = getattr(self, 'extension_expiry_date', False)
        expiry_date = extension_expiry_date or self.expiry_date
        delay_in_days = self.type_id.automated_action_delay or 0
        return today + timedelta(delay_in_days) >= expiry_date

    def _is_delay_between_leads_reached(self):
        """Determine if the minimum delay between 2 leads for the customer was reached.

        :rtype: bool
        """
        today = datetime.now().date()
        delay_in_days = self._get_delay_between_leads()
        previous_lead = self._find_last_generated_lead_for_partner()
        return (
            not previous_lead or
            previous_lead.create_date.date() + timedelta(delay_in_days) <= today
        )

    def _bind_warranty_to_last_generated_lead(self):
        """Bind the current warranty to the previous generated action."""
        existing_lead = self._find_last_generated_lead_for_partner()
        self.lead_id = existing_lead
        self.message_post_with_view(
            'sale_warranty_lead_on_expiry.lead_already_exist_message',
            values={'lead': existing_lead, 'partner': self.partner_id},
            subtype_id=self.env.ref('mail.mt_note').id
        )

    def _get_delay_between_leads(self):
        """Get the delay in days between 2 actions for the same customer.

        :rtype: int
        """
        return (
            self.env.user.company_id.warranty_delay_between_leads or
            DEFAULT_DELAY_BETWEEN_LEADS
        )

    def _find_last_generated_lead_for_partner(self):
        """Find the last lead generated from a warranty for this customer.

        :rtype: crm.lead record
        """
        return self.env['crm.lead'].search([
            ('generated_from_warranty', '=', True),
            ('partner_id', 'child_of', self.partner_id.id),
            ('company_id', '=', self.company_id.id),
        ], limit=1, order='id desc')

    def _generate_new_lead(self):
        """Generate a new lead for this warranty."""
        lead_vals = self._get_crm_lead_values()
        new_lead = self.env['crm.lead'].create(lead_vals)
        new_lead.message_post_with_view(
            'mail.message_origin_link',
            values={'self': new_lead, 'origin': self},
            subtype_id=self.env.ref('mail.mt_note').id
        )
        self.lead_id = new_lead
        self.message_post_with_view(
            'sale_warranty_lead_on_expiry.lead_created_message',
            values={'lead': new_lead},
            subtype_id=self.env.ref('mail.mt_note').id
        )

    def _get_crm_lead_values(self):
        return {
            'name': self._format_lead_name(),
            'partner_id': self.partner_id.id,
            'team_id': self.type_id.sales_team_id.id,
            'generated_from_warranty': True,
            'company_id': self.company_id.id,
            'type': 'opportunity',
        }

    def _format_lead_name(self):
        """Format the name of the lead generated for this warranty.

        :rtype: str
        """
        return _("End Of Warranty {}").format(self.reference)
