# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CommissionPayrollPeriodSelection(models.TransientModel):
    _name = "commission.payroll.period.selection"
    _description = "Commission Payroll Period Selection"

    target_id = fields.Many2one("commission.target")
    period = fields.Many2one("payroll.period")

    def confirm(self):
        amount = self.target_id.commissions_total
        self._create_payroll_entry(self.target_id, self.period, amount)
        self.target_id.already_paid += amount

    def _create_payroll_entry(self, target, period, amount):
        return self.env["payroll.preparation.line"].create(
            {
                "company_id": target.company_id.id,
                "period_id": period.id,
                "employee_id": target.employee_id.id,
                "target_id": target.id,
                "amount": amount,
            }
        )
