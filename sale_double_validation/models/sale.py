# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(
        selection_add=[("to_approve", "To Approve"), ("draft",)])

    def is_amount_to_approve(self):
        self.ensure_one()
        currency = self.company_id.currency_id
        limit_amount = self.company_id.so_double_validation_amount
        limit_amount = currency.compute(limit_amount, self.currency_id)
        return (
            float_compare(
                limit_amount,
                self.amount_total,
                precision_rounding=self.currency_id.rounding,
            )
            <= 0
        )

    def is_to_approve(self):
        self.ensure_one()
        return (
            self.company_id.so_double_validation == "two_step"
            and self.is_amount_to_approve()
            and not self.user_has_groups("sales_team.group_sale_manager")
        )

    @api.model
    def create(self, vals):
        obj = super().create(vals)
        if obj.is_to_approve():
            obj.state = "to_approve"
        return obj

    def action_approve(self):
        self.write({"state": "draft"})
