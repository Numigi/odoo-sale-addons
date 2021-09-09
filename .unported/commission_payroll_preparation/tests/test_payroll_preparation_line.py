# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import TestPayrollCase


class TestPayrollPreparationLine(TestPayrollCase):
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

        cls.payroll_line = cls.env["payroll.preparation.line"].create(
            {
                "company_id": cls.target.company_id.id,
                "period_id": cls.period.id,
                "employee_id": cls.target.employee_id.id,
                "commission_target_id": cls.target.id,
                "amount": 1000,
            }
        )

    def test_payroll_line_count(self):
        assert self.target.payroll_line_count == 1
