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
    invoiced_amount = fields.Monetary(compute="_compute_invoiced_amount", store=True)
    target_amount = fields.Monetary(required=True)
    fixed_rate = fields.Float()
    commissions_total = (
        fields.Monetary()
    )  # contains the employee revenue from commissions when the category rate is fixed

    def compute(self):
        for target in self:
            target._update_invoices()
            target._compute_invoiced_amount()
            target._compute_commissions_total()

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

    @api.depends("invoice_ids")
    def _compute_invoiced_amount(self):
        self.invoiced_amount = sum(
            inv.amount_total_company_signed for inv in self.invoice_ids
        )

    def _compute_commissions_total(self):
        if self.category_id.rate_type == "fixed":
            self._compute_target_commissions_fixed()
        else:
            # if not fixed, update commission_target_rates instead
            self._compute_target_commissions_interval()

    def _compute_target_commissions_fixed(self):
        self.commissions_total = self.invoiced_amount * self.fixed_rate / 100

    def _compute_target_commissions_interval(self):
        self._update_rates()

    def _update_rates(self):
        for rate in self.rate_ids:
            rate._compute_rate()
