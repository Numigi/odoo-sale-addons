from odoo.tests import common, tagged
from datetime import date, timedelta


@tagged("post_install", "-at_install")
class TestCronNotification(common.TransactionCase):

    def setUp(self):
        super(TestCronNotification, self).setUp()

        self.stage_draft = self.env["crm.stage"].create({"name": "Draft"})

        self.team = self.env["crm.team"].create({"name": "Test Team"})

        self.user1 = self.env["res.users"].create(
            {
                "name": "Test User 1",
                "login": "test_user_1",
                "email": "test1@example.com",
            }
        )

        self.user2 = self.env["res.users"].create(
            {
                "name": "Test User 2",
                "login": "test_user_2",
                "email": "test2@example.com",
            }
        )

        self.team.member_ids = [(6, 0, [self.user1.id, self.user2.id])]

        self.activity_type = self.env["mail.activity.type"].create(
            {"name": "To Do", "category": "default"}
        )

        self.model = self.env["ir.model"].search([("model", "=", "crm.lead")], limit=1)

    def test_cron_notification_ten_days_old_leads(self):

        old_create_date = date.today() - timedelta(days=11)
        old_lead = self.env["crm.lead"].create(
            {
                "name": "Old Lead",
                "stage_id": self.stage_draft.id,
                "team_id": self.team.id,
                "create_date": old_create_date.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        recent_create_date = date.today() - timedelta(days=5)
        recent_lead = self.env["crm.lead"].create(
            {
                "name": "Recent Lead",
                "stage_id": self.stage_draft.id,
                "team_id": self.team.id,
                "create_date": recent_create_date.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        self.env["crm.lead"].cron_notification_ten_days()

        activities_old_lead = self.env["mail.activity"].search(
            [("res_id", "=", old_lead.id), ("res_model", "=", "crm.lead")]
        )

        activities_recent_lead = self.env["mail.activity"].search(
            [("res_id", "=", recent_lead.id), ("res_model", "=", "crm.lead")]
        )

        self.assertEqual(
            len(activities_old_lead),
            2,
            "Devrait avoir 2 activités (un par utilisateur) pour le vieux lead",
        )
        self.assertEqual(
            len(activities_recent_lead),
            0,
            "Ne devrait pas avoir d'activité pour le lead récent",
        )

        for activity in activities_old_lead:
            self.assertEqual(activity.activity_type_id, self.activity_type)
            self.assertIn("Old Lead", activity.summary)
            self.assertIn(self.team.member_ids.ids, [activity.user_id.id])

    def test_cron_notification_ten_days_no_leads(self):

        activity_count_before = self.env["mail.activity"].search_count([])
        self.env["crm.lead"].cron_notification_ten_days()
        activity_count_after = self.env["mail.activity"].search_count([])

        self.assertEqual(
            activity_count_before,
            activity_count_after,
            "Ne devrait pas créer d'activités sans leads éligibles",
        )

    def test_cron_notification_ten_days_different_stage(self):
        stage_won = self.env["crm.stage"].create({"name": "Won"})
        old_create_date = date.today() - timedelta(days=11)
        lead_other_stage = self.env["crm.lead"].create(
            {
                "name": "Lead Other Stage",
                "stage_id": stage_won.id,
                "team_id": self.team.id,
                "create_date": old_create_date.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        self.env["crm.lead"].cron_notification_ten_days()

        activities = self.env["mail.activity"].search(
            [("res_id", "=", lead_other_stage.id), ("res_model", "=", "crm.lead")]
        )

        self.assertEqual(
            len(activities),
            0,
            "Ne devrait pas créer d'activité pour les leads d'autres stages",
        )
