# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestCRMAssignByArea(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Users
        context = dict(cls.env.context, no_reset_password=True)
        cls.env = cls.env(context=context)
        cls.user_1 = cls.env["res.users"].create({"name": "User 1", "login": "user_1"})
        cls.user_2 = cls.env["res.users"].create({"name": "User 2", "login": "user_2"})

        # Territories
        cls.territory_has_salesperson_1 = cls.env["res.territory"].create(
            {"name": "1", "salesperson_id": cls.user_1.id}
        )
        cls.territory_has_salesperson_2 = cls.env["res.territory"].create(
            {"name": "2", "salesperson_id": cls.user_2.id}
        )
        cls.territory_no_salesperson = cls.env["res.territory"].create({"name": "3"})

        # FSA
        cls.fsa_no_salesperson = cls.env["forward.sortation.area"].create(
            {
                "name": "100",
                "territory_ids": [(6, 0, [cls.territory_no_salesperson.id])],
            }
        )
        cls.fsa_one_salesperson = cls.env["forward.sortation.area"].create(
            {
                "name": "200",
                "territory_ids": [(6, 0, [cls.territory_has_salesperson_1.id])],
            }
        )
        cls.fsa_several_salespersons = cls.env["forward.sortation.area"].create(
            {
                "name": "300",
                "territory_ids": [
                    (
                        6,
                        0,
                        [
                            cls.territory_has_salesperson_1.id,
                            cls.territory_has_salesperson_2.id,
                        ],
                    )
                ],
            }
        )

        # Partner
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.crm = cls.env["crm.lead"].create(
            {"name": "Pipeline", "partner_id": cls.partner.id}
        )

        wizard_env = cls.env["assign.salesperson.by.area.wizard"]
        cls.wizard_crm_env = wizard_env.with_context(
            active_id=cls.crm.id, active_model="crm.lead"
        )
        cls.wizard_partner_env = wizard_env.with_context(
            active_id=cls.partner.id, active_model="res.partner"
        )

    def test_crm_cannot_assign_salesperson_if_crm_has_no_customer(self):
        with self.assertRaises(ValidationError):
            self.env["crm.lead"].create(
                {"name": "Pipeline"}
            ).action_assign_salesperson()

    def test_crm_assign_salesperson_case_no_salesperson_to_assign(self):
        self.partner.zip = "100000"
        with Form(self.wizard_crm_env) as wizard:
            res = wizard.save()
            with self.assertRaises(AssertionError):
                res.action_confirm()

    def test_crm_assign_salesperson_case_one_salesperson_to_assign(self):
        self.partner.zip = "200000"
        with Form(self.wizard_crm_env) as wizard:
            res = wizard.save()
            res.action_confirm()
            self.assertEqual(self.crm.user_id, self.user_1)

    def test_crm_assign_salesperson_case_several_salesperson_to_assign(self):
        self.partner.zip = "300000"
        with Form(self.wizard_crm_env) as wizard:
            wizard.salesperson_id = self.user_1
            res = wizard.save()
            res.action_confirm()
            self.assertEqual(self.crm.user_id, self.user_1)

    def test_partner_assign_salesperson_case_no_salesperson_to_assign(self):
        self.partner.zip = "100000"
        with Form(self.wizard_partner_env) as wizard:
            res = wizard.save()
            with self.assertRaises(AssertionError):
                res.action_confirm()

    def test_partner_assign_salesperson_case_one_salesperson_to_assign(self):
        self.partner.zip = "200000"
        with Form(self.wizard_partner_env) as wizard:
            res = wizard.save()
            res.action_confirm()
            self.assertEqual(self.partner.user_id, self.user_1)

    def test_partner_assign_salesperson_case_several_salesperson_to_assign(self):
        self.partner.zip = "300000"
        with Form(self.wizard_partner_env) as wizard:
            wizard.salesperson_id = self.user_1
            res = wizard.save()
            res.action_confirm()
            self.assertEqual(self.partner.user_id, self.user_1)

    def test_salesperson_name_get_with_context(self):
        self.assertEqual(
            self.user_1.with_context(
                assign_salesperson_by_area_territory_ids=[
                    (6, 0, self.territory_has_salesperson_1.ids)
                ]
            ).name_get(),
            [
                (
                    self.user_1.id,
                    "{} ({})".format(
                        self.user_1.name, self.territory_has_salesperson_1.display_name
                    ),
                )
            ],
        )
