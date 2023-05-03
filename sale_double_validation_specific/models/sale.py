# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models,fields
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    to_approve = fields.Boolean(compute='compute_to_approve')
    to_confirm = fields.Boolean(compute='compute_to_confirm')

    def compute_to_approve(self):
        self.ensure_one()
        currency = self.company_id.currency_id
        limit_amount = self.company_id.so_double_validation_amount
        limit_amount = currency.compute(limit_amount, self.currency_id)
        if self.state in ['draft'] and self.is_to_approve() and self.state != "to_approve":
            self.to_approve = True
        else:
            self.to_approve = False

    def compute_to_confirm(self):
        self.ensure_one()
        if self.user_has_groups("sales_team.group_sale_manager") and self.state in ["draft", "to_approve"]:
            self.to_confirm = True
        elif not self.user_has_groups("sales_team.group_sale_manager")\
                and not self.is_to_approve() and self.state == "draft":
            self.to_confirm = True
        else:
            self.to_confirm = False

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
        self.write({"state": "to_approve"})
        #self.is_approved = True




