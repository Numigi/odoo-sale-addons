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
        amount = self._compute_target_commissions_within_period()
        return self.env["payroll.preparation.line"].create(
            {
                "company_id": self.target_id.company_id.id,
                "period_id": self.period.id,
                "employee_id": self.target_id.employee_id.id,
                "target_id": self.target_id.id,
                "amount": amount,
            }
        )

    def _compute_target_commissions_within_period(self):
        initial_date_start = self.target_id.date_start
        initial_date_end = self.target_id.date_end

        self._compute_target_from_dates(
            self.period.date_from, self.period.date_to
        )
        commissions_total = self.target_id.commissions_total
        self._compute_target_from_dates(initial_date_start, initial_date_end)
        
        self._update_target(commissions_total)

        return commissions_total

    def _compute_target_from_dates(self, date_from, date_to):
        self.target_id.date_start = date_from
        self.target_id.date_end = date_to
        self.target_id.compute()

    def _update_target(self, paid_amount):
        if not self.target_id.already_paid:
            self.target_id.already_paid = paid_amount
        else:
            self.target_id.already_paid += paid_amount
        self.target_id.status = "in_progress"
