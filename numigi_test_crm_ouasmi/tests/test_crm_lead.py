import pytest
from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta

@pytest.mark.usefixtures("env")
class TestCrmLead(TransactionCase):

    def setUp(self):
        super().setUp()
        self.team = self.env['crm.team'].create({'name': 'Team Test'})
        self.lead = self.env['crm.lead'].create({
            'name': 'Lead plus 10 jours',
            'type': 'opportunity',
            'team_id': self.team.id,
            'stage_id': self.env['crm.stage'].search([], limit=1).id,
        })

    def test_notify_stale_opportunities__should_post_message(self):
        old_date = datetime.now() - timedelta(days=15)
        self.lead.write({
            'date_last_stage_update': old_date,
            'create_date': old_date
        })

        self.env['crm.lead'].notify_stale_opportunities()
        assert self.lead.message_ids, "Aucune notification n’a été envoyée pour une opportunité dormante"

    def test_notify_stale_opportunities__should_skip_recent_leads(self):
        self.lead.write({'date_last_stage_update': datetime.now()})
        initial_message_count = len(self.lead.message_ids)
        self.env['crm.lead'].notify_stale_opportunities()
        assert len(self.lead.message_ids) == initial_message_count, \
            "Une opportunité récente ne devrait pas recevoir de notification."
