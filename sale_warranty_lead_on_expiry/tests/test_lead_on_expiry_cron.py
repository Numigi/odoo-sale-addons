# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from freezegun import freeze_time
from odoo.tests.common import SavepointCase
from ..models.common import DEFAULT_DELAY_BETWEEN_LEADS as LEAD_DELAY


class LeadOnExpiryCronCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Set queue job to no delay for testing
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        cls.env.user.company_id.warranty_delay_between_leads = LEAD_DELAY

        cls.customer = cls.env["res.partner"].create({"name": "My Customer"})

        cls.team = cls.env["crm.team"].create({"name": "Team A"})

        cls.warranty_6_months = cls.env["sale.warranty.type"].create(
            {
                "name": "6 Months Parts",
                "duration_in_months": 6,
                "description": "Warranted 6 months on parts",
                "automated_action": True,
                "sales_team_id": cls.team.id,
                "automated_action_delay": 0,
            }
        )

        cls.product_a = cls.env["product.product"].create(
            {
                "name": "My Product",
                "tracking": "serial",
                "type": "product",
            }
        )

        cls.warranty = cls._create_warranty()

    @classmethod
    def _find_lead(cls):
        return cls.env["crm.lead"].search([("partner_id", "=", cls.customer.id)])

    @classmethod
    def _run_cron(cls):
        cls.env.ref(
            "sale_warranty_lead_on_expiry.lead_on_expiry_cron"
        ).method_direct_trigger()

    @classmethod
    def _create_warranty(cls):
        today = datetime.now().date()
        return cls.env["sale.warranty"].create(
            {
                "partner_id": cls.customer.id,
                "product_id": cls.product_a.id,
                "type_id": cls.warranty_6_months.id,
                "state": "active",
                "activation_date": today - timedelta(90),
                "expiry_date": today - timedelta(30),
            }
        )


class TestLeadOnExpiryCron(LeadOnExpiryCronCase):

    def test_if_no_existing_lead__new_lead_created(self):
        assert not self._find_lead()
        self._run_cron()
        lead = self._find_lead()
        assert len(lead) == 1

    def test_if_existing_lead__no_new_lead_created(self):
        self._run_cron()
        previous_lead = self._find_lead()

        new_warranty = self._create_warranty()
        self._run_cron()
        assert new_warranty.lead_id == previous_lead

    def test_if_warranty_has_different_customer__new_lead_created(self):
        self._run_cron()
        previous_lead = self._find_lead()

        new_warranty = self._create_warranty()
        new_warranty.partner_id = self.customer.copy()
        self._run_cron()
        assert new_warranty.lead_id
        assert new_warranty.lead_id != previous_lead

    def test_if_days_to_trigger_not_reached__no_lead_created(self):
        self.warranty.expiry_date = datetime.now().date() + timedelta(30)
        self.warranty_6_months.automated_action_delay = 29
        self._run_cron()
        assert not self.warranty.lead_id

    def test_if_days_to_trigger_reached__new_lead_created(self):
        self.warranty.expiry_date = datetime.now().date() + timedelta(30)
        self.warranty_6_months.automated_action_delay = 30
        self._run_cron()
        assert self.warranty.lead_id

    def test_generated_lead_type_is_opportunity(self):
        self._run_cron()
        lead = self._find_lead()
        assert lead.type == "opportunity"


class TestWarrantiesWithExtension(LeadOnExpiryCronCase):
    """Test the warranties end in case of a warranty extension.

    This test class requires the module sale_warranty_extension
    to be installed.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        today = datetime.now().date()
        cls.warranty.write(
            {
                "activation_date": today - timedelta(150),
                "expiry_date": today - timedelta(120),
                "extension_start_date": today + timedelta(60),
                "extension_expiry_date": today + timedelta(90),
            }
        )

    def test_if_days_to_trigger_not_reached__no_lead_created(self):
        self.warranty_6_months.automated_action_delay = 89
        self._run_cron()
        assert not self.warranty.lead_id

    def test_if_days_to_trigger_reached__new_lead_created(self):
        self.warranty_6_months.automated_action_delay = 90
        self._run_cron()
        assert self.warranty.lead_id


class TestDelayBetweenLeadCreation(LeadOnExpiryCronCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._run_cron()
        cls.previous_lead = cls._find_lead()
        assert cls.previous_lead

    def test_after_delay__new_lead_created(self):
        with freeze_time(datetime.now() + timedelta(LEAD_DELAY)):
            new_warranty = self._create_warranty()
            self._run_cron()
            assert new_warranty.lead_id
            assert new_warranty.lead_id != self.previous_lead

    def test_one_day_before_delay__no_new_lead_created(self):
        with freeze_time(datetime.now() + timedelta(LEAD_DELAY - 1)):
            new_warranty = self._create_warranty()
            self._run_cron()
            assert new_warranty.lead_id
            assert new_warranty.lead_id == self.previous_lead

    def test_after_custom_delay__new_lead_created(self):
        custom_delay = 100
        self.env.user.company_id.warranty_delay_between_leads = custom_delay

        with freeze_time(datetime.now() + timedelta(custom_delay)):
            new_warranty = self._create_warranty()
            self._run_cron()
            assert new_warranty.lead_id
            assert new_warranty.lead_id != self.previous_lead

    def test_one_day_before_custom_delay__new_lead_created(self):
        custom_delay = 100
        self.env.user.company_id.warranty_delay_between_leads = custom_delay

        with freeze_time(datetime.now() + timedelta(custom_delay - 1)):
            new_warranty = self._create_warranty()
            self._run_cron()
            assert new_warranty.lead_id
            assert new_warranty.lead_id == self.previous_lead
