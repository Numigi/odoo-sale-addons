# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    commission_target_ids = fields.Many2many(
        "commission.target",
        "commission_target_invoice_line_rel",
        "invoice_line_id",
        "target_id",
    )

    commission_target_count = fields.Integer(
        compute="_compute_commission_target_count",
        store=True,
    )

    @api.depends('commission_target_ids.state')
    def _compute_commission_target_count(self):
        for line in self:
            targets = line.commission_target_ids.filtered(
                lambda t: t.state not in ("draft", "cancelled")
            )
            line.commission_target_count = len(targets)
