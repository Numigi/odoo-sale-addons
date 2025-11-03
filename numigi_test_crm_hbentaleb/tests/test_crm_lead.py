# -*- coding: utf-8 -*-
from datetime import date

from odoo.addons.numigi_test_crm_hbentaleb.tests.common import TestCRM


class TestCRMLead(TestCRM):
    def test_crm_lead_cron_true(self):
        self.opp_id.create_date = date(2022, 9, 2)
        self.crm_lead_model._cron_send_notification_to_members()
        self.assertTrue(self.opp_id.is_notification_created)

    def test_crm_lead_cron_false(self):
        self.crm_lead_model._cron_send_notification_to_members()
        self.assertFalse(self.opp_id.is_notification_created)

    def test_crm_lead_cron_true2(self):
        self.lead_1.date_conversion = date(2022, 9, 2)
        self.crm_lead_model._cron_send_notification_to_members()
        self.assertTrue(self.lead_1.is_notification_created)

    def test_crm_lead_cron_false2(self):
        self.crm_lead_model._cron_send_notification_to_members()
        self.assertFalse(self.lead_1.is_notification_created)
