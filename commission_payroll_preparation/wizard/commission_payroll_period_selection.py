# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CommissionPayrollPeriodSelection(models.TransientModel):
    _name = "commission.payroll.period.selection"
    _description = "Commission Payroll Period Selection"

    target_id = fields.Many2one("commission.target")
    period = fields.Many2one("payroll.period")

    def confirm(self):
        self._create_payroll_entry(self.target_id, self.period)

    def _create_payroll_entry(self, target, period):
        amount = self.target_id.commissions_total
        return self.env["payroll.preparation.line"].create(
            {
                "company_id": self.target_id.company_id.id,
                "period_id": self.period.id,
                "employee_id": self.target_id.employee_id.id,
                "target_id": self.target_id.id,
                "amount": amount,
            }
        )
