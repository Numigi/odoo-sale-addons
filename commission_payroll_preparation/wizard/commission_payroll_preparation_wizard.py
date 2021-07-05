# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CommissionPayrollPreparationWizard(models.TransientModel):
    _name = "commission.payroll.preparation.wizard"
    _description = "Commission Payroll Preparation Wizard"

    target_ids = fields.Many2many(
        "commission.target",
        "commission_payroll_preparation_wizard_target_rel",
        "wizard_id",
        "target_id",
    )
    period = fields.Many2one("payroll.period", required=True)

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["target_ids"] = [(6, 0, self._context.get("active_ids") or [])]
        return defaults

    def confirm(self):
        for target in self.target_ids:
            if target.state != "confirmed":
                raise ValidationError(_("You generate a payroll entry for a target in a state other than 'confirmed'."))
            self._create_payroll_entry(target)

    def _create_payroll_entry(self, target):
        return self.env["payroll.preparation.line"].create(
            {
                "company_id": target.company_id.id,
                "period_id": self.period.id,
                "employee_id": target.employee_id.id,
                "commission_target_id": target.id,
                "amount": target.total_amount,
            }
        )
