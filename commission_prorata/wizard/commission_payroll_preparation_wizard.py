# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class CommissionPayrollPreparationWizard(models.TransientModel):
    _inherit = "commission.payroll.preparation.wizard"

    target_ids = fields.Many2many(
        "commission.target",
        "commission_payroll_preparation_wizard_target_rel",
        "wizard_id",
        "target_id",
    )
    prorata_days_worked = fields.Float(default=1)

    
    def confirm():
        super().confirm()
