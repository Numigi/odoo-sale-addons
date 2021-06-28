# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from functools import reduce


class CommissionTarget(models.Model):
    _name = "commission.target"
    _description = "Commission Target"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft"
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
    date_start = fields.Date(related="date_range_id.date_start", store=True)
    date_end = fields.Date(related="date_range_id.date_end", store=True)
    invoice_ids = fields.Many2many(
        "account.invoice", "commission_target_invoice_rel", "target_id", "invoice_id"
    )
    child_target_ids = fields.Many2many(
        "commission.target", "commission_target_child_rel", "parent_id", "child_id"
    )
    target_amount = fields.Monetary(required=True)
    fixed_rate = fields.Float()
    base_amount = fields.Monetary(readonly=True)
    commissions_total = fields.Monetary(readonly=True)

    def compute(self):
        for target in self._sorted_by_category_dependency():
            target._update_base_amount()
            target._update_commissions_total()

    def _sorted_by_category_dependency(self):
        categories = list(self.mapped("category_id")._sorted_by_dependencies())
        return self.sorted(lambda t: categories.index(t.category_id))

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

    def _compute_my_base_amount(self):
        # return sum(inv.amount_total_company_signed for inv in self.invoice_ids)
        return sum(
            self._compute_invoice_amount(invoice) for invoice in self.invoice_ids
        )

    def _compute_invoice_amount(self, invoice):
        return sum(
            line.price_subtotal_signed
            for line in invoice.invoice_line_ids
            if self._should_use_invoice_line(line)
        )

    def _should_use_invoice_line(self, line):
        is_included_line = self._is_included_invoice_line(line)
        is_excluded_line = self._is_excluded_invoice_line(line)
        return is_included_line and not is_excluded_line

    def _is_included_invoice_line(self, line):
        included = self.category_id.included_tag_ids
        return not included or bool(included & line.analytic_tag_ids)

    def _is_excluded_invoice_line(self, line):
        excluded = self.category_id.excluded_tag_ids
        return bool(excluded & line.analytic_tag_ids)

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
            and child.category_id in self.category_id.child_category_ids
        )
        return children

    def _compute_my_team_commissions(self):
        return self._compute_my_team_commissions_total()

    def _compute_my_team_commissions_total(self):
        return sum(child.commissions_total for child in self.child_target_ids)

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

    @api.model
    def create(self, vals):
        if vals.get('name', 'New Target') == 'New Target':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'commission.target.reference') or 'New'
        result = super(CommissionTarget, self).create(vals)
        return result

    @api.onchange("category_id")
    def onchange_category_id(self):
        if self.category_id.rate_type == "fixed":
            self._onchange_category_id_fixed()
        elif self.category_id.rate_type == "interval":
            self._onchange_category_id_interval()

    def _onchange_category_id_fixed(self):
        self.fixed_rate = self.category_id.fixed_rate

    def _onchange_category_id_interval(self):
        self.rate_ids = self._copy_target_rates_from_category()

    def _copy_target_rates_from_category(self):
        res = self.env["commission.target.rate"]

        for category_rate in self.category_id.rate_ids:
            res |= self._copy_target_rate_from_category_rate(category_rate)

        return res

    def _copy_target_rate_from_category_rate(self, category_rate):
        return self.env["commission.target.rate"].new(
            {
                "slice_from": category_rate.slice_from,
                "slice_to": category_rate.slice_to,
                "commission_percentage": category_rate.commission_percentage
            }
        )
