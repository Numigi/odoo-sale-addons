# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class CommissionTargetRate(models.Model):
    _name = "commission.target.rate"
    _description = "Commission Target Rate"

    target_id = fields.Many2one("commission.target", required=True)
    slice_from = fields.Float(required=True)
    slice_to = fields.Float(required=True)
    commission_percentage = fields.Float(required=True)
    max_amount = fields.Monetary()
    completion_rate = (
        fields.Float()
    )  # <field name="progress" widget="progressbar"/> pour que ce soit une progress bar
    subtotal = fields.Monetary()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.user.company_id, required=True
    )
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")

    def _compute_rate(self):
        total = self.target_id.invoiced_amount
        target = self.target_id.target_amount

        slice_from = self.slice_from / 100 * target
        slice_to = self.slice_to / 100 * target

        if slice_to - slice_from <= 0:
            self.completion_rate = 0
            return

        if total <= slice_from:
            self.completion_rate = 0
            self.subtotal = 0

        elif total <= slice_to:
            full_slice = slice_to - slice_from
            completion = total - slice_from
            self.completion_rate = completion / full_slice
            self.subtotal = completion * self.commission_percentage / 100

        else:
            self.completion_rate = 1
            self.subtotal = (slice_to - slice_from) * self.commission_percentage / 100
