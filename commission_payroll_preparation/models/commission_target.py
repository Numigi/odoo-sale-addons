# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class CommissionTarget(models.Model):
    _inherit = "commission.target"

    payroll_line_ids = fields.One2many("payroll.preparation.line", "target_id", readonly=True)
    already_paid = fields.Monetary(compute="_compute_already_paid", store=True)
    left_to_pay = fields.Monetary(compute="_compute_left_to_pay", store=True)

    @api.depends("payroll_line_ids")
    def _compute_already_paid(self):
        self.already_paid = sum(line.amount for line in self.payroll_line_ids)

    @api.depends("already_paid")
    def _compute_left_to_pay(self):
        self.left_to_pay = self.commissions_total - self.already_paid
