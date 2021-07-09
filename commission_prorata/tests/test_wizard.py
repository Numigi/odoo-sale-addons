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

    def test_create_payroll_default_prorata(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()

        self.wizard.confirm()

        created_payroll = self.env["payroll.preparation.line"].search([("company_id", "=", self.target.company_id.id)])

        assert created_payroll.amount == invoiced_amount * self.fixed_rate
        assert self.target.prorata_days_worked == 1
        assert self.target.eligible_amount == invoiced_amount * self.fixed_rate

    def test_create_payroll_prorata(self):
        invoiced_amount = 500
        self._create_invoice(amount=invoiced_amount)
        self.target.compute()

        prorata = 0.5
        self.wizard.prorata_days_worked = prorata
        self.wizard.confirm()

        created_payroll = self.env["payroll.preparation.line"].search([("company_id", "=", self.target.company_id.id)])

        assert created_payroll.amount == invoiced_amount * self.fixed_rate * self.wizard.prorata_days_worked
        assert self.target.prorata_days_worked == prorata
        assert self.target.eligible_amount == invoiced_amount * self.fixed_rate * self.wizard.prorata_days_worked
