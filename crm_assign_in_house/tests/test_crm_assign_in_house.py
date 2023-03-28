# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import SavepointCase
from odoo.tests import tagged


@tagged("post_install")
class TestCRMAssignByArea(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        context = dict(cls.env.context, no_reset_password=True)
        cls.env = cls.env(context=context)
        cls.salesperson = cls.env["res.users"].create(
            {"name": "Salesperson", "login": "salesperson"}
        )

    def test_partner_not_in_house_salesperson_not_required(self):
        with Form(self.env["res.partner"]) as partner_form:
            partner_form.name = "Partner"
            partner_form.save()

    def test_partner_in_house_salesperson_required(self):
        with Form(self.env["res.partner"]) as partner_form:
            partner_form.name = "Partner"
            partner_form.in_house = True
            with self.assertRaises(AssertionError):
                try:
                    partner_form.save()
                except AssertionError as e:
                    self.assertTrue(
                        "user_id is a required field ({'required': [('in_house', '=', True)]})"
                        in str(e)
                    )
                    raise
            partner_form.user_id = self.salesperson
            partner_form.save()

    def test_crm_onchange_not_in_house_customer_not_set_salesperson(self):
        not_in_house_customer = self.env["res.partner"].create(
            {"name": "Customer", "in_house": False, "user_id": self.salesperson.id}
        )
        with Form(self.env["crm.lead"]) as crm_form:
            crm_form.name = "Pipeline"
            crm_form.partner_id = not_in_house_customer
            res = crm_form.save()
            self.assertNotEqual(res.user_id, self.salesperson)

    def test_crm_onchange_in_house_customer_set_salesperson(self):
        in_house_customer = self.env["res.partner"].create(
            {"name": "Customer", "in_house": True, "user_id": self.salesperson.id}
        )
        with Form(self.env["crm.lead"]) as crm_form:
            crm_form.name = "Pipeline"
            crm_form.partner_id = in_house_customer
            res = crm_form.save()
            self.assertEqual(res.user_id, self.salesperson)
