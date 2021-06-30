# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
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

    def test_create_payroll(self):
        self.wizard.confirm()
        created_payroll = self.env["payroll.preparation.line"].search([("company_id", "=", self.target.company_id.id)])
        assert (
            created_payroll.period_id == self.period
            and created_payroll.employee_id == self.employee
            and created_payroll.amount == 0
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

    def test_create_payroll_target_already_paid(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()

        self.wizard.confirm()

        assert self.target.already_paid == invoiced_amount * self.fixed_rate

    def test_create_payroll_target_left_to_pay(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()

        self.wizard.confirm()

        assert (
            self.target.left_to_pay
            == self.target.total_amount - self.target.already_paid
        )

    def test_create_payroll_assigns_target_id(self):
        self.wizard.confirm()
        created_payroll = self.env["payroll.preparation.line"].search([("company_id", "=", self.target.company_id.id)])
        assert created_payroll.target_id == self.target


    def test_create_payroll_not_confirmed_state(self):
        self.target.state = "draft"
        with pytest.raises(ValidationError):
            self.wizard.confirm()

    def test_payroll_line_amount(self):
        self.wizard.confirm()
        self.target._compute_already_paid()

        assert self.target.payroll_line_amount == 1