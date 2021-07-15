# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.commission_payroll_preparation.tests.common import TestPayrollCase
from datetime import date


class ProrataCase(TestPayrollCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.target_amount = 1000
        cls.fixed_rate = 0.05
        cls.invoiced_amount = 500
        cls.target = cls.env["commission.target"].create(
            {
                "employee_id": cls.employee.id,
                "category_id": cls.category.id,
                "target_amount": cls.target_amount,
                "date_range_id": cls.date_range.id,
                "rate_type": "fixed",
                "fixed_rate": cls.fixed_rate,
                "state": "confirmed",
            }
        )
        cls.target.total_amount = cls.invoiced_amount * cls.fixed_rate

        cls.wizard = cls.env["commission.payroll.preparation.wizard"].create(
            {
                "target_ids": [(6, 0, [cls.target.id])],
                "period": cls.period.id,
            }
        )
