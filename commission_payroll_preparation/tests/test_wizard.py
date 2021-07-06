# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from .common import TestPayrollCase


class TestWizard(TestPayrollCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.target_amount = 1000
        cls.fixed_rate = 0.05
        cls.target = cls.env["commission.target"].create(
            {
                "employee_id": cls.employee.id,
                "category_id": cls.category.id,
                "target_amount": cls.target_amount,
                "date_range_id": cls.date_range.id,
                "rate_type": "fixed",
                "fixed_rate": cls.fixed_rate,
                "state": "confirmed"
            }
        )

        cls.wizard = cls.env["commission.payroll.preparation.wizard"].create(
            {
                "target_ids": [(6, 0, [cls.target.id])],
                "period": cls.period.id,
            }
        )

    def test_create_payroll_with_amount(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()

        self.wizard.confirm()

        created_payroll = self.env["payroll.preparation.line"].search([("company_id", "=", self.target.company_id.id)])
        assert (
            created_payroll.period_id == self.period
            and created_payroll.employee_id == self.employee
            and created_payroll.amount == invoiced_amount * self.fixed_rate
        )

    def test_create_payroll_target_already_generated(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()

        self.wizard.confirm()

        assert self.target.already_generated == invoiced_amount * self.fixed_rate

    def test_create_payroll_target_left_to_generate(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()

        self.wizard.confirm()

        assert (
            self.target.left_to_generate
            == self.target.total_amount - self.target.already_generated
        )

    def test_create_payroll_multiple(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()
        self.wizard.confirm()

        self._create_invoice(amount=invoiced_amount)
        self.target.compute()
        self.wizard.confirm()

        assert self.target.left_to_generate == self.target.total_amount - self.target.already_generated
        assert self.target.already_generated == 2 * (invoiced_amount * self.fixed_rate)

    def test_payroll_entry_not_created_when_0_left_to_pay(self):
        invoiced_amount = 1000
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()
        self.wizard.confirm()

        with pytest.raises(ValidationError):
            self.wizard.confirm()


    def test_create_payroll_assigns_target_id(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()
        self.wizard.confirm()
        created_payroll = self.env["payroll.preparation.line"].search([("company_id", "=", self.target.company_id.id)])
        assert created_payroll.commission_target_id == self.target

    def test_create_payroll_not_confirmed_state(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()

        self.target.state = "draft"
        with pytest.raises(ValidationError):
            self.wizard.confirm()

    def test_payroll_lines_shown_on_wizard_confirm(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()

        action = self.wizard.confirm()
        domain = action["domain"]
        assert domain == [("id", "in", self.target.payroll_line_ids.ids)]
