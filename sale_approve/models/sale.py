# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import _, api, models,fields
from odoo.tools import float_compare
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    to_approve = fields.Boolean(compute='compute_to_approve')
    to_confirm = fields.Boolean(compute='compute_to_confirm')
    state = fields.Selection(selection_add=[("to_approve", "Approved Quotation")])

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
        for order in self:
            if order.is_to_approve() and order.state == "draft":
                raise UserError(_("Cannot confirm this quotation without sale manager's approbation"))
        return super(SaleOrder, self).action_confirm()

    def action_approve(self):
        _logger.info("Approve Quotation")
        self.write({"state": "to_approve"})




