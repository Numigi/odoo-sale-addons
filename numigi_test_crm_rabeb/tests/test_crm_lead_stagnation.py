from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import timedelta


class TestCrmLeadStagnation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.env["crm.stage"].search([]).unlink()
        cls.stage_1 = cls.env["crm.stage"].create({
            "name": "New",
            "sequence": 1
        })
        cls.stage_2 = cls.env["crm.stage"].create({
            "name": "Qualified",
            "sequence": 2
        })
        cls.team = cls.env["crm.team"].create({"name": "Sales"})

    def test_find_stagnant__old_opportunity_in_first_stage(self):
        old_date = fields.Datetime.now() - timedelta(days=11)
        opp = self.env["crm.lead"].create({
            "name": "Old",
            "type": "opportunity",
            "stage_id": self.stage_1.id,
            "create_date": old_date,
            "team_id": self.team.id
        })

        result = self.env["crm.lead"]._find_stagnant_opportunities()

        assert opp in result

    def test_find_stagnant__recent_opportunity_excluded(self):
        recent_date = fields.Datetime.now() - timedelta(days=5)
        opp = self.env["crm.lead"].create({
            "name": "Recent",
            "type": "opportunity",
            "stage_id": self.stage_1.id,
            "create_date": recent_date,
            "team_id": self.team.id
        })

        result = self.env["crm.lead"]._find_stagnant_opportunities()

        assert opp not in result

    def test_find_stagnant__opportunity_in_second_stage_excluded(self):
        old_date = fields.Datetime.now() - timedelta(days=11)
        opp = self.env["crm.lead"].create({
            "name": "Advanced",
            "type": "opportunity",
            "stage_id": self.stage_2.id,
            "create_date": old_date,
            "team_id": self.team.id
        })

        result = self.env["crm.lead"]._find_stagnant_opportunities()

        assert opp not in result

    def test_find_stagnant__opportunity_without_team_excluded(self):
        old_date = fields.Datetime.now() - timedelta(days=11)
        opp = self.env["crm.lead"].create({
            "name": "No Team",
            "type": "opportunity",
            "stage_id": self.stage_1.id,
            "create_date": old_date
        })

        result = self.env["crm.lead"]._find_stagnant_opportunities()

        assert opp not in result

    def test_find_stagnant__lead_excluded(self):
        old_date = fields.Datetime.now() - timedelta(days=11)
        lead = self.env["crm.lead"].create({
            "name": "Lead",
            "type": "lead",
            "stage_id": self.stage_1.id,
            "create_date": old_date,
            "team_id": self.team.id
        })

        result = self.env["crm.lead"]._find_stagnant_opportunities()

        assert lead not in result

    def test_find_stagnant__no_stage_returns_empty(self):
        self.env["crm.stage"].search([]).unlink()

        result = self.env["crm.lead"]._find_stagnant_opportunities()

        assert len(result) == 0

    def test_notify_stagnant__returns_true(self):
        result = self.env["crm.lead"]._notify_stagnant_opportunities()

        assert result is True

    def test_send_notifications__email_sent_with_template(self):
        template = self.env["mail.template"].create({
            "name": "Stale",
            "model_id": self.env.ref("crm.model_crm_lead").id,
            "subject": "Stagnant",
            "body_html": "<p>Stagnant</p>"
        })
        self.env["ir.model.data"].create({
            "name": "email_template_stale_opportunity",
            "module": "numigi_test_crm_rabeb",
            "model": "mail.template",
            "res_id": template.id
        })
        opp = self.env["crm.lead"].create({
            "name": "Opp",
            "type": "opportunity"
        })
        initial_count = self.env["mail.mail"].search_count([])

        self.env["crm.lead"]._send_notifications(opp)

        assert self.env["mail.mail"].search_count([]) > initial_count

    def test_send_notifications__no_error_without_template(self):
        opp = self.env["crm.lead"].create({
            "name": "Opp",
            "type": "opportunity"
        })

        self.env["crm.lead"]._send_notifications(opp)