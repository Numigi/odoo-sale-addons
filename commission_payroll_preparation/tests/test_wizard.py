# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import TestPayrollCase
from datetime import date


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
                "fixed_rate": cls.fixed_rate,
            }
        )

        cls.wizard = cls.env["commission.payroll.period.selection"].create(
            {
                "target_id": cls.target.id,
                "period": cls.period.id,
            }
        )

    def test_create_payroll(self):
        self.wizard.confirm()
        created_payroll = self.env["payroll.preparation.line"].search([])
        assert (
            created_payroll.company_id == self.company
            and created_payroll.period_id == self.period
            and created_payroll.employee_id == self.employee
            and created_payroll.amount == 0
        )

    def test_create_payroll_with_amount(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()

        self.wizard.confirm()

        created_payroll = self.env["payroll.preparation.line"].search([])
        assert (
            created_payroll.company_id == self.company
            and created_payroll.period_id == self.period
            and created_payroll.employee_id == self.employee
            and created_payroll.amount == invoiced_amount * self.fixed_rate
        )

    def test_create_payroll_wrong_date(self):
        invoiced_amount = 500
        early_date_to = date(2021, 2, 10)
        self._create_invoice(_date=self.date_middle, amount=invoiced_amount)
        self.target.compute()

        self.period.date_to = early_date_to
        self.wizard.confirm()

        created_payroll = self.env["payroll.preparation.line"].search([])
        assert (
            created_payroll.company_id == self.company
            and created_payroll.period_id == self.period
            and created_payroll.employee_id == self.employee
            and created_payroll.amount == 0
        )

    def test_create_payroll_adds_to_already_paid(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()

        self.wizard.confirm()

        assert self.target.already_paid == invoiced_amount * self.fixed_rate

    def test_create_payroll_assigns_target_id(self):
        self.wizard.confirm()
        created_payroll = self.env["payroll.preparation.line"].search([])
        assert created_payroll.target_id == self.target

    def test_create_payroll_target_in_progress(self):
        self.wizard.confirm()
        assert self.target.status == "in_progress"
