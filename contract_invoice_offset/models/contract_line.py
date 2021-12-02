# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class ContractLine(models.Model):

    _inherit = "contract.line"

    invoicing_offset_interval = fields.Integer()
    invoicing_offset_rule_type = fields.Selection(
        [
            ("daily", "Day(s)"),
            ("weekly", "Week(s)"),
            ("monthly", "Month(s)"),
        ],
        default="monthly",
        string="Invoicing Offset Type",
    )

    def _compute_recurring_invoicing_offset(self):
        for rec in self:
            rec.recurring_invoicing_offset = rec._get_invoicing_offset()

    def _check_recurring_next_date_start_date(self):
        pass

    def _check_last_date_invoiced(self):
        pass

    @api.onchange("invoicing_offset_interval", "invoicing_offset_rule_type")
    def _onchange_invoicing_offset(self):
        for line in self.filtered('date_start'):
            line._update_recurring_next_date()

    def _update_recurring_next_date(self):
        self.recurring_next_date = self.get_next_invoice_date(
            self.next_period_date_start,
            self.recurring_invoicing_type,
            self.recurring_invoicing_offset,
            self.recurring_rule_type,
            self.recurring_interval,
            max_date_end=self.date_end,
        )

    def _get_invoicing_offset(self):
        rule_type = self.invoicing_offset_rule_type

        if rule_type == "daily":
            return self._get_daily_invoicing_offset()

        elif rule_type == "weekly":
            return self._get_weekly_invoicing_offset()

        if rule_type == "monthly":
            return self._get_montly_invoicing_offset()

    def _get_daily_invoicing_offset(self):
        return -self.invoicing_offset_interval

    def _get_weekly_invoicing_offset(self):
        return -self.invoicing_offset_interval * 7

    def _get_montly_invoicing_offset(self):
        delta = relativedelta(months=self.invoicing_offset_interval)
        invoicing_date = self.next_period_date_start - delta
        return (invoicing_date - self.next_period_date_start).days
