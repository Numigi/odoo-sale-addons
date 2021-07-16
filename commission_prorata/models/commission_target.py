# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class CommissionTarget(models.Model):
    _inherit = "commission.target"

    prorata_days_worked = fields.Float(default=1, readonly=True)
    eligible_amount = fields.Monetary(default=0, readonly=True)

    def compute(self):
        super().compute()
        for target in self:
            target._update_eligible_amount()

    def _update_eligible_amount(self):
        self.eligible_amount = self.total_amount * self.prorata_days_worked

    @api.depends("eligible_amount", "already_generated")
    def _compute_left_to_generate(self):
        for target in self:
            target.left_to_generate = target.eligible_amount - target.already_generated
