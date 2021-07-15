# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class CommissionTarget(models.Model):
    _inherit = "commission.target"

    prorata_days_worked = fields.Float(default=1, readonly=True)
    eligible_amount = fields.Monetary(
        readonly=True, compute="_compute_eligible_amount", store=True
    )

    @api.depends("eligible_amount", "already_generated")
    def _compute_left_to_generate(self):
        for target in self:
            target.left_to_generate = target.eligible_amount - target.already_generated
