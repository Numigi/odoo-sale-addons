from odoo.tests.common import TransactionCase


class TestCrmLeadTeam(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.team = cls.env["crm.team"].create({"name": "Sales"})

    def test_lead__team_assigned(self):
        lead = self.env["crm.lead"].create({
            "name": "Lead",
            "team_id": self.team.id
        })

        assert lead.team_id == self.team

    def test_lead__team_changed(self):
        team2 = self.env["crm.team"].create({"name": "Sales 2"})
        lead = self.env["crm.lead"].create({
            "name": "Lead",
            "team_id": self.team.id
        })
        lead.write({"team_id": team2.id})

        assert lead.team_id == team2