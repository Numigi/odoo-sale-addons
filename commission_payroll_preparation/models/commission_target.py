# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class CommissionTarget(models.Model):
    _inherit = "commission.target"

    already_paid = fields.Monetary(default=0)
    left_to_pay = fields.Monetary(compute="_compute_left_to_pay", store=True)

    @api.depends("already_paid")
    def _compute_left_to_pay(self):
        self.left_to_pay = self.commissions_total - self.already_paid
