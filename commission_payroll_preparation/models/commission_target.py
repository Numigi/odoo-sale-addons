# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class CommissionTarget(models.Model):
    _inherit = "commission.target"

    payroll_line_ids = fields.One2many(
        "payroll.preparation.line", "commission_target_id", readonly=True,
        group="payroll_preparation.group_user"
    )
    payroll_line_count = fields.Integer(
        compute="_compute_payroll_line_count",
        groups="payroll_preparation.group_user"
    )

    already_generated = fields.Monetary(compute="_compute_already_generated", store=True)
    left_to_generate = fields.Monetary(compute="_compute_left_to_generate", store=True)

    def _compute_payroll_line_count(self):
        for target in self:
            target.payroll_line_count = len(target.payroll_line_ids)

    @api.depends("payroll_line_ids.amount")
    def _compute_already_generated(self):
        for target in self:
            target.already_generated = sum(line.amount for line in target.payroll_line_ids)
            target.payroll_line_amount = len(target.payroll_line_ids)

    @api.depends("total_amount", "already_generated")
    def _compute_left_to_generate(self):
        for target in self:
            target.left_to_generate = target.total_amount - target.already_generated
