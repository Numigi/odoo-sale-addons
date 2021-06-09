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
    category_id = fields.Many2one("commission.category")
    rate_type = fields.Selection(related="category_id.rate_type", store=True)
    date_start = fields.Date()
    date_end = fields.Date()
    invoice_ids = fields.Many2many(
        "account.invoice", "commission_target_invoice_rel", "target_id", "invoice_id"
    )
    target_amount = fields.Monetary(required=True)
    invoiced_amount = fields.Monetary(compute="_compute_invoiced_amount", store=True)
    commissions_total = fields.Monetary(
        compute="_compute_commissions_total", store=True
    )
    fixed_rate = fields.Float()
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")

    def compute(self):
        for target in self:
            target.invoice_ids = target._find_invoices()

    def _find_invoices(self):
        invoices = self.env["account.invoice"].search(
            [
                ("date_invoice", ">=", self.date_start),
            ]
        )
        if self.category_id.basis == "personal":
            return self._filter_invoices_personal(invoices)
        else:
            return self._filter_invoices_team(invoices)
        
    def _filter_invoices_personal(self, invoices):
        return invoices.filtered(
            lambda inv: inv.company_id == self.company_id
            and inv.user_id == self.employee_id.user_id
            and inv.date_invoice <= self.date_end
            and inv.type not in ("in_invoice", "in_refund")
            and inv.state not in ("draft", "cancel")
        )

    def _filter_invoices_team(self, invoices):
        return invoices
        # TODO

    @api.depends("invoiced_amount", "fixed_rate")
    def _compute_commissions_total(self):
        for target in self:
            if target.category_id.rate_type == "fixed":
                self._compute_target_commissions_fixed(target)
            else:
                self._compute_target_commissions_interval(target)

    def _compute_target_commissions_fixed(self, target):
        target.commissions_total = (
            target.invoiced_amount * target.fixed_rate / 100
        )

    def _compute_target_commissions_interval(self, target):
        pass
        # TODO

    @api.depends("invoice_ids")
    def _compute_invoiced_amount(self):
        for target in self:
            target.invoiced_amount = sum(
                inv.amount_total_company_signed for inv in target.invoice_ids
            )
