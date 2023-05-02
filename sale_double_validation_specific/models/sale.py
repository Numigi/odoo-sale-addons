# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models,fields
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    to_approve = fields.Boolean(compute='compute_to_approve')
    is_approved = fields.Boolean("Is approved")


    def compute_to_approve(self):
        self.ensure_one()
        currency = self.company_id.currency_id
        limit_amount = self.company_id.so_double_validation_amount
        limit_amount = currency.compute(limit_amount, self.currency_id)

        if self.state in ['draft'] and self.is_to_approve() and not self.is_approved:
            self.to_approve = True
        else:
            self.to_approve = False

    @api.model
    def create(self, vals):
        obj = super().create(vals)
        if obj.is_to_approve():
            obj.state = "draft"
        return obj

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        return res

    def action_approve(self):
        self.is_approved = True




