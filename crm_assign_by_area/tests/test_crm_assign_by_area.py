# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import SavepointCase, post_install


@post_install(True)
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

    def test_crm_cannot_assign_salesperson_if_crm_has_no_customer(self):
        with self.assertRaises(ValidationError):
            self.env["crm.lead"].create(
                {"name": "Pipeline"}
            ).action_assign_salesperson()

    def test_crm_cannot_assign_salesperson_if_partner_has_no_territory(self):
        with self.assertRaises(ValidationError):
            self.crm.action_assign_salesperson()

    def test_partner_cannot_assign_salesperson_if_partner_has_no_territory(self):
        with self.assertRaises(ValidationError):
            self.partner.action_assign_salesperson()

    def test_crm_assign_salesperson_case_no_salesperson_to_assign(self):
        self.partner.zip = "100000"
        context = {"active_id": self.crm.id, "active_model": "crm.lead"}
        context.update(self.crm.action_assign_salesperson().get("context"))
        with Form(
            self.env["assign.salesperson.by.area.wizard"].with_context(context)
        ) as wizard:
            res = wizard.save()
            self.assertEqual(
                res.wizard_msg,
                "There is no salesperson to assign. The partner's territories might not link to any salesperson.",
            )
            with self.assertRaises(ValidationError):
                res.action_confirm()

    def test_crm_assign_salesperson_case_one_salesperson_to_assign(self):
        self.partner.zip = "200000"
        context = {"active_id": self.crm.id, "active_model": "crm.lead"}
        context.update(self.crm.action_assign_salesperson().get("context"))
        with Form(
            self.env["assign.salesperson.by.area.wizard"].with_context(context)
        ) as wizard:
            res = wizard.save()
            self.assertEqual(
                res.wizard_msg,
                "%s will be assigned to the opportunity. Do you want to continue?"
                % self.user_1.display_name,
            )
            res.action_confirm()
            self.assertEqual(self.crm.user_id, self.user_1)

    def test_crm_assign_salesperson_case_several_salesperson_to_assign(self):
        self.partner.zip = "300000"
        context = {"active_id": self.crm.id, "active_model": "crm.lead"}
        context.update(self.crm.action_assign_salesperson().get("context"))
        with Form(
            self.env["assign.salesperson.by.area.wizard"].with_context(context)
        ) as wizard:
            wizard.salesperson_id = self.user_2
            res = wizard.save()
            self.assertEqual(
                res.wizard_msg,
                "Several salespersons could be assigned depending on the partner's territories. Please choose the right seller.",
            )
            res.action_confirm()
            self.assertEqual(self.crm.user_id, self.user_2)
        with Form(
            self.env["assign.salesperson.by.area.wizard"].with_context(context)
        ) as wizard:
            wizard.salesperson_id = self.user_1
            res = wizard.save()
            res.action_confirm()
            self.assertEqual(self.crm.user_id, self.user_1)

    def test_partner_assign_salesperson_case_no_salesperson_to_assign(self):
        self.partner.zip = "100000"
        context = {"active_id": self.partner.id, "active_model": "res.partner"}
        context.update(self.partner.action_assign_salesperson().get("context"))
        with Form(
            self.env["assign.salesperson.by.area.wizard"].with_context(context)
        ) as wizard:
            res = wizard.save()
            self.assertEqual(
                res.wizard_msg,
                "There is no salesperson to assign. The partner's territories might not link to any salesperson.",
            )
            with self.assertRaises(ValidationError):
                res.action_confirm()

    def test_partner_assign_salesperson_case_one_salesperson_to_assign(self):
        self.partner.zip = "200000"
        context = {"active_id": self.partner.id, "active_model": "res.partner"}
        context.update(self.partner.action_assign_salesperson().get("context"))
        with Form(
            self.env["assign.salesperson.by.area.wizard"].with_context(context)
        ) as wizard:
            res = wizard.save()
            self.assertEqual(
                res.wizard_msg,
                "%s will be assigned to the opportunity. Do you want to continue?"
                % self.user_1.display_name,
            )
            res.action_confirm()
            self.assertEqual(self.partner.user_id, self.user_1)

    def test_partner_assign_salesperson_case_several_salesperson_to_assign(self):
        self.partner.zip = "300000"
        context = {"active_id": self.partner.id, "active_model": "res.partner"}
        context.update(self.partner.action_assign_salesperson().get("context"))
        with Form(
            self.env["assign.salesperson.by.area.wizard"].with_context(context)
        ) as wizard:
            wizard.salesperson_id = self.user_2
            res = wizard.save()
            self.assertEqual(
                res.wizard_msg,
                "Several salespersons could be assigned depending on the partner's territories. Please choose the right seller.",
            )
            res.action_confirm()
            self.assertEqual(self.partner.user_id, self.user_2)
        with Form(
            self.env["assign.salesperson.by.area.wizard"].with_context(context)
        ) as wizard:
            wizard.salesperson_id = self.user_1
            res = wizard.save()
            res.action_confirm()
            self.assertEqual(self.partner.user_id, self.user_1)
