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
    completion = (
        fields.Float()
    )  # <field name="progress" widget="progressbar"/> pour que ce soit une progress bar
    subtotal = fields.Monetary()
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.user.company_id, required=True
    )
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")

    def _compute_rate(self):
        total = self.target_id.commissions_total
        target = self.target_id.target_amount
        minimum = self.slice_from / 100 * target
        quantity = (self.slice_to - self.slice_from)/100 * target
        if quantity <= 0:
            self.completion = 0
            self.subtotal = 0
            print(f"QUANTITY WAS 0 !!!")
            return

        total = max(0, total - minimum)
        result = min(1, total / quantity)

        self.completion = result
        self.subtotal = self.max_amount * result
