# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import AccessError
from odoo.osv.expression import AND


class CommissionTarget(models.Model):
    _name = "commission.target"
    _description = "Commission Target"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name desc"

    name = fields.Char(string="Reference", readonly=True, copy=False, default="")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        readonly=True,
        required=True,
        copy=False,
        track_visibility="onchange",
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Agent",
        readonly=True,
        required=True,
        track_visibility="onchange",
        states={"draft": [("readonly", False)]},
    )
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.user.company_id, required=True
    )
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")
    category_id = fields.Many2one(
        "commission.category",
        readonly=True,
        states={"draft": [("readonly", False)]},
        required=True,
        track_visibility="onchange",
    )
    basis = fields.Selection(
        related="category_id.basis",
        store=True,
    )
    rate_type = fields.Selection(
        related="category_id.rate_type",
        store=True,
    )
    rate_ids = fields.One2many(
        "commission.target.rate",
        "target_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_range_id = fields.Many2one(
        "date.range",
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)]},
        track_visibility="onchange",
    )
    date_start = fields.Date(related="date_range_id.date_start", store=True)
    date_end = fields.Date(related="date_range_id.date_end", store=True)
    last_compute_date = fields.Datetime()
    invoice_line_ids = fields.Many2many(
        "account.invoice.line",
        "commission_target_invoice_line_rel",
        "target_id",
        "invoice_line_id",
    )
    child_target_ids = fields.Many2many(
        "commission.target",
        "commission_target_child_rel",
        "parent_id",
        "child_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    target_amount = fields.Monetary(
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        track_visibility="onchange",
    )
    fixed_rate = fields.Float(
        readonly=True,
        states={"draft": [("readonly", False)]},
        track_visibility="onchange",
    )
    invoiced_amount = fields.Monetary(
        "Total Amount On Admissible Invoice Lines", readonly=True, copy=False
    )
    child_commission_amount = fields.Monetary(
        "Total Amount On Team Commissions", readonly=True, copy=False
    )
    base_amount = fields.Monetary(readonly=True, copy=False)
    total_amount = fields.Monetary(readonly=True, copy=False)

    show_invoices = fields.Boolean(compute="_compute_show_invoices")
    show_child_targets = fields.Boolean(compute="_compute_show_child_targets")

    @api.multi
    def copy(self, default=None):
        target = super().copy(default)

        for rate in self.rate_ids:
            rate.copy({"target_id": target.id})

        return target

    def _compute_show_invoices(self):
        for target in self:
            target.show_invoices = target.basis == "my_sales"

    def _compute_show_child_targets(self):
        for target in self:
            target.show_child_targets = target.basis == "my_team_commissions"

    def compute(self):
        self.check_extended_security_read()
        self = self.sudo()

        for target in self._sorted_by_category_dependency():
            target._update_base_amount()
            target._update_total_amount()

        self.last_compute_date = datetime.now()

    def _sorted_by_category_dependency(self):
        categories = list(self.mapped("category_id")._sorted_by_dependencies())
        return self.sorted(lambda t: categories.index(t.category_id))

    def _update_base_amount(self):
        if self.category_id.basis == "my_sales":
            self._update_base_amount_my_sales()
        elif self.category_id.basis == "my_team_commissions":
            self._update_base_amount_my_team_commissions()

    def _update_base_amount_my_sales(self):
        self.invoice_line_ids = self._get_invoice_lines()
        self.invoiced_amount = self._compute_invoiced_amount()
        self.base_amount = self.invoiced_amount

    def _get_invoice_lines(self):
        invoices = self._get_invoices()
        return invoices.mapped("invoice_line_ids").filtered(
            lambda l: self._should_use_invoice_line(l)
        )

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

    def _compute_invoiced_amount(self):
        return sum(line.price_subtotal_signed for line in self.invoice_line_ids)

    def _should_use_invoice_line(self, line):
        is_included_line = self._is_included_invoice_line(line)
        is_excluded_line = self._is_excluded_invoice_line(line)
        return is_included_line and not is_excluded_line

    def _is_included_invoice_line(self, line):
        included = self.category_id.included_tag_ids
        tags = line.sale_line_ids.order_id.so_tag_ids
        return not included or bool(included & tags)

    def _is_excluded_invoice_line(self, line):
        excluded = self.category_id.excluded_tag_ids
        tags = line.sale_line_ids.order_id.so_tag_ids
        return bool(excluded & tags)

    def _update_base_amount_my_team_commissions(self):
        self._get_child_targets()
        self.child_target_ids = self._get_child_targets()
        self.child_commission_amount = self._compute_child_commission_amount()
        self.base_amount = self.child_commission_amount

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
            and child.company_id == self.company_id
        )
        return children

    def _compute_child_commission_amount(self):
        return sum(child.total_amount for child in self.child_target_ids)

    def _update_total_amount(self):
        if self.category_id.rate_type == "fixed":
            self._update_total_amount_fixed()
        elif self.category_id.rate_type == "interval":
            self._update_total_amount_interval()

    def _update_total_amount_fixed(self):
        self.total_amount = self._compute_total_amount_fixed()

    def _compute_total_amount_fixed(self):
        total = self.base_amount * self.fixed_rate
        return total

    def _update_total_amount_interval(self):
        self._update_rates()
        self.total_amount = self._compute_total_amount_interval()

    def _update_rates(self):
        for rate in self.rate_ids:
            rate._update_rate()

    def _compute_total_amount_interval(self):
        total = sum(rate.subtotal for rate in self.rate_ids)
        return total

    @api.model
    def create(self, vals):
        target = super().create(vals)
        target.name = target._get_next_sequence_number()
        return target

    def _get_next_sequence_number(self):
        return (
            self.env["ir.sequence"]
            .with_context(force_company=self.company_id.id)
            .next_by_code("commission.target.reference")
        )

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
                "commission_percentage": category_rate.commission_percentage,
            }
        )

    def set_confirmed_state(self):
        for target in self:
            target.state = "confirmed"

    def set_done_state(self):
        for target in self:
            target.state = "done"

    def set_cancelled_state(self):
        for target in self:
            target.state = "cancelled"

    def set_draft_state(self):
        for target in self:
            target.state = "draft"

    def view_invoice_lines(self):
        action = self.env.ref("commission.action_invoice_lines").read()[0]
        action["name"] = _("Invoice Lines")
        action["domain"] = [("id", "in", self.invoice_line_ids.ids)]
        return action

    def view_child_targets(self):
        action = self.env.ref("commission.action_target").read()[0]
        action["name"] = _("Team Commissions")
        action["domain"] = [("id", "in", self.child_target_ids.ids)]
        return action

    def check_extended_security_all(self):
        super().check_extended_security_all()

        if self._user_is_manager():
            self._check_manager_access()

        elif self._user_is_team_manager():
            self._check_team_manager_access()

        else:
            self._check_user_access()

    def _user_is_manager(self):
        return self.env.user.has_group("commission.group_manager")

    def _user_is_team_manager(self):
        return self.env.user.has_group("commission.group_team_manager")

    def _check_manager_access(self):
        pass

    def _check_team_manager_access(self):
        user = self.env.user
        departments = self._get_user_managed_departments()

        for target in self.sudo():
            employee = target.employee_id

            is_own_target = employee.user_id == user
            is_own_department = employee.department_id in departments

            if not (is_own_target or is_own_department):
                raise AccessError(
                    _(
                        "You are not allowed to access the target {} because "
                        "it is either not your own target or a target of a member "
                        "of your team."
                    ).format(target.display_name)
                )

    def _check_user_access(self):
        user = self.env.user

        for target in self.sudo():
            if target.employee_id.user_id != user:
                raise AccessError(
                    _(
                        "You are not allowed to access the target {} because "
                        "it is not your own target."
                    ).format(target.display_name)
                )

    def _get_user_managed_departments(self):
        return (
            self.env["hr.department"]
            .sudo()
            .search(
                [
                    ("manager_id", "in", self.env.user.employee_ids.ids),
                ]
            )
        )

    def get_extended_security_domain(self):
        result = super().get_extended_security_domain()

        company_domain = self._get_company_domain()

        if self._user_is_manager():
            extra_domain = self._get_manager_domain()

        elif self._user_is_team_manager():
            extra_domain = self._get_team_manager_domain()

        else:
            extra_domain = self._get_user_domain()

        return AND([result, company_domain, extra_domain])

    def _get_company_domain(self):
        return [
            ("company_id", "=", self.env.user.company_id.id),
        ]

    def _get_manager_domain(self):
        return []

    def _get_team_manager_domain(self):
        departments = self._get_user_managed_departments()
        return [
            "|",
            ("employee_id.department_id", "in", departments.ids),
            ("employee_id.user_id", "=", self.env.user.id),
        ]

    def _get_user_domain(self):
        return [
            ("employee_id.user_id", "=", self.env.user.id),
        ]

    @api.model
    def get_read_access_actions(self):
        res = super().get_read_access_actions()
        res.append("compute")
        return res
