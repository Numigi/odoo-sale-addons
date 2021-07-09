# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class CommissionPayrollPreparationWizard(models.TransientModel):
    _inherit = "commission.payroll.preparation.wizard"

    prorata_days_worked = fields.Float(default=1)
    
    def confirm(self):
        self._update_target_ids()
        super().confirm()
        

    def _update_target_ids(self):
        for target in self.target_ids:
            target.prorata_days_worked = self.prorata_days_worked
            target.eligible_amount = target.total_amount * target.prorata_days_worked