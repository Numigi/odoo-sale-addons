# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class CommissionTarget(models.Model):
    _name = "commission.target"
    _description = "Commission Target"

    name = fields.Char()
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ]
    )
    employee_id = fields.Many2one("hr.employee", string="Agent")
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.user.company_id, required=True
    )
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")
    category_id = fields.Many2one("commission.category")
    rate_type = fields.Selection(related="category_id.rate_type", store=True)
    rate_ids = fields.One2many("commission.target.rate", "target_id")
    date_range_id = fields.Many2one("date.range")
    invoice_ids = fields.Many2many(
        "account.invoice", "commission_target_invoice_rel", "target_id", "invoice_id"
    )
    child_target_ids = fields.Many2many(
        "commission.target", "commission_target_child_rel", "parent_id", "child_id"
    )
    target_amount = fields.Monetary(required=True)
    fixed_rate = fields.Float()
    base_amount = fields.Monetary()
    commissions_total = fields.Monetary()

    def compute(self):
        for target in self:  # ._sort_by_children_first():
            target._update_base_amount()
            target._update_commissions_total()

    """def _sort_by_children_first(self):
        return self.sorted(key=lambda r: not r in self.child_target_ids)"""

    def _update_base_amount(self):
        if self.category_id.basis == "my_sales":
            self._update_base_amount_my_sales()
        elif self.category_id.basis == "my_team_commissions":
            self._update_base_amount_my_team_commissions()

    def _update_base_amount_my_sales(self):
        self.invoice_ids = self._get_invoices()
        self.base_amount = self._compute_my_base_amount()

    def _get_invoices(self):
        invoices = self.env["account.invoice"].search(
            [
                ("date_invoice", ">=", self.date_range_id.date_start),
            ]
        )
        invoices = invoices.filtered(
            lambda inv: inv.company_id == self.company_id
            and inv.user_id == self.employee_id.user_id
            and inv.date_invoice <= self.date_range_id.date_end
            and inv.type not in ("in_invoice", "in_refund")
            and inv.state not in ("draft", "cancel")
        )

        return invoices

    def _compute_my_base_amount(self):
        return sum(inv.amount_total_company_signed for inv in self.invoice_ids)

    def _update_base_amount_my_team_commissions(self):
        self._get_child_targets()
        self.child_target_ids = self._get_child_targets()
        self.base_amount = self._compute_my_team_commissions()

    def _get_child_targets(self):
        children = (
            self.env["commission.target"].search(
                [
                    ("employee_id.department_id.manager_id", "=", self.employee_id.id),
                ]
            )
            - self
        )
        children = children.filtered(
            lambda child: child.date_range_id == self.date_range_id
        )
        return children

    def _compute_my_team_commissions(self):
        total = 0
        for target in self.child_target_ids:
            target.compute()
            total += target.commissions_total
        return total

    def _update_commissions_total(self):
        if self.category_id.rate_type == "fixed":
            self._update_commissions_total_fixed()
        elif self.category_id.rate_type == "interval":
            self._update_commissions_total_interval()

    def _update_commissions_total_fixed(self):
        self.commissions_total = self._compute_commissions_total_fixed()

    def _compute_commissions_total_fixed(self):
        return self.base_amount * self.fixed_rate

    def _update_commissions_total_interval(self):
        self._update_rates()
        self.commissions_total = self._compute_commissions_total_interval()

    def _update_rates(self):
        for rate in self.rate_ids:
            rate._update_rate()

    def _compute_commissions_total_interval(self):
        return sum(rate.subtotal for rate in self.rate_ids)
