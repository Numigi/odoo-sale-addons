# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class CommissionTarget(models.Model):
    _inherit = "commission.target"

    payroll_line_ids = fields.One2many("payroll.preparation.line", "commission_target_id", readonly=True)
    payroll_line_amount = fields.Integer(compte="_compute_payroll_line_amount", store=True)
    already_generated = fields.Monetary(compute="_compute_already_generated", store=True)
    left_to_generate = fields.Monetary(compute="_compute_left_to_generate", store=True)

    @api.depends("payroll_line_ids")
    def _compute_already_generated(self):
        for target in self:
            target.already_generated = sum(line.amount for line in target.payroll_line_ids)
            target.payroll_line_amount = len(target.payroll_line_ids)

    @api.depends("already_generated")
    def _compute_left_to_generate(self):
        for target in self:
            target.left_to_generate = target.total_amount - target.already_generated
