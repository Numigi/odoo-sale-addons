from odoo import api, fields, models
from datetime import timedelta

STAGNATION_THRESHOLD_DAYS = 10


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model
    def _notify_stagnant_opportunities(self):
        """Main entry point: find stagnant opportunities and notify their teams."""
        opportunities = self._find_stagnant_opportunities()
        self._send_notifications(opportunities)
        return True

    def _find_stagnant_opportunities(self):
        """Find opportunities that stayed too long in the initial stage.

        Returns:
            recordset(crm.lead): Opportunities created more than
            STAGNATION_THRESHOLD_DAYS ago and still in the first stage.
        """
        # Compute the oldest allowed creation date
        limit_date = fields.Datetime.now() - timedelta(days=STAGNATION_THRESHOLD_DAYS)
        # Get the initial CRM stage (lowest sequence)
        initial_stage = self.env["crm.stage"].search([], order="sequence asc", limit=1)
        # Safety check: ensure a stage exists
        if not initial_stage:
            return self.env["crm.lead"]
        # Search for stagnant opportunities
        stagnant_opps = self.search(
            [
                ("type", "=", "opportunity"),
                ("stage_id", "=", initial_stage.id),
                ("create_date", "<=", limit_date),
                ("team_id", "!=", False),
            ]
        )
        return stagnant_opps

    def _send_notifications(self, opportunities):
        """Send email notifications for stagnant opportunities."""
        template = self.env.ref(
            "numigi_test_crm_rabeb.email_template_stale_opportunity",
            raise_if_not_found=False,
        )
        if not template:
            return
        for opportunity in opportunities:
            template.send_mail(opportunity.id, force_send=True)
