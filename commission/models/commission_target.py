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
    date_start = fields.Date()
    date_end = fields.Date()
    invoice_ids = fields.Many2many(
        "account.invoice", "commission_target_invoice_rel", "target_id", "invoice_id"
    )
    child_target_ids = fields.Many2many(
        "commission.target", "commission_target_child_rel", "parent_id", "child_id"
    )
    target_amount = fields.Monetary(required=True)
    fixed_rate = fields.Float()
    invoiced_amount = fields.Monetary()
    commissions_total = fields.Monetary()

    """def compute(self):
        for target in self:
            if target.category_id.basis == "personal":
                target._compute_target_personal()
            else:
                target._compute_target_team()

    def _compute_target_personal(self):
        self._update_invoices()
        self._compute_invoiced_amount()
        self._compute_commissions_total_personal()

    def _update_invoices(self):
        invoices = self.env["account.invoice"].search(
            [
                ("date_invoice", ">=", self.date_start),
            ]
        )
        invoices = invoices.filtered(
            lambda inv: inv.company_id == self.company_id
            and inv.user_id == self.employee_id.user_id
            and inv.date_invoice <= self.date_end
            and inv.type not in ("in_invoice", "in_refund")
            and inv.state not in ("draft", "cancel")
        )
        self.invoice_ids = invoices

        return invoices

    def _compute_invoiced_amount(self):
        self.invoiced_amount = sum(
            inv.amount_total_company_signed for inv in self.invoice_ids
        )

    def _compute_commissions_total_personal(self):
        if self.category_id.rate_type == "fixed":
            self._compute_target_commissions_fixed()
        else:
            self._update_rates()

    def _compute_target_commissions_fixed(self):
        self.commissions_total = self.invoiced_amount * self.fixed_rate

    def _compute_target_team(self):
        self._update_child_targets()
        total = self._compute_commissions_total_team()
        self._update_commissions_team(total)

    def _update_child_targets(self):
        targets = self.env["commission.target"].search(
            [
                ("employee_id.department_id.manager_id", "=", self.employee_id.id),
            ]
        )
        self.child_target_ids = targets - self

    def _compute_commissions_total_team(self):
        total = 0
        for target in self.child_target_ids:
            target.compute()
            total += target.commissions_total
        return total

    def _update_commissions_team(self, total):
        if self.category_id.rate_type == "fixed":
            self._compute_commissions_team_fixed(total)
        else:
            self._compute_commissions_team_interval(total)

    def _compute_commissions_team_fixed(self, total):
        self.commissions_total = total * self.fixed_rate

    def _compute_commissions_team_interval(self, total):
        self.team_total = total
        self._update_rates()

    def _update_rates(self):
        for rate in self.rate_ids:
            rate._compute_completion_rate()
            rate._compute_subtotal()"""

    ###########################

    def compute(self):
        for target in self:
            target._update_invoiced_amount()
            target._update_commissions_total()

    def _update_invoiced_amount(self):
        if self.category_id.basis == "my_sales":
            self._update_invoiced_amount_my_sales()
        elif self.category_id.basis == "my_team_commissions":
            self._update_invoiced_amount_my_team_commissions()

    def _update_invoiced_amount_my_sales(self):
        self.invoice_ids = self._get_invoices()
        self.invoiced_amount = self._compute_my_invoiced_amount()

    def _get_invoices(self):
        invoices = self.env["account.invoice"].search(
            [
                ("date_invoice", ">=", self.date_start),
            ]
        )
        invoices = invoices.filtered(
            lambda inv: inv.company_id == self.company_id
            and inv.user_id == self.employee_id.user_id
            and inv.date_invoice <= self.date_end
            and inv.type not in ("in_invoice", "in_refund")
            and inv.state not in ("draft", "cancel")
        )

        return invoices

    def _compute_my_invoiced_amount(self):
        return sum(
            inv.amount_total_company_signed for inv in self.invoice_ids
        )

    def _update_invoiced_amount_my_team_commissions(self):
        self._get_child_targets()
        self.child_target_ids = self._get_child_targets()
        self.invoiced_amount = self._compute_my_team_commissions()

    def _get_child_targets(self):
        return self.env["commission.target"].search(
            [
                ("employee_id.department_id.manager_id", "=", self.employee_id.id),
            ]
        ) - self

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
        return self.invoiced_amount * self.fixed_rate
        
    def _update_commissions_total_interval(self):
        self._update_rates()
        self.commissions_total = self._compute_commissions_total_interval()
        
    def _update_rates(self):
        for rate in self.rate_ids:
            rate._update_rate()

    def _compute_commissions_total_interval(self):
        return sum(rate.subtotal for rate in self.rate_ids)
