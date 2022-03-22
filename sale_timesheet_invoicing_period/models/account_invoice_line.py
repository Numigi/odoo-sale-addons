# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.osv.expression import AND


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    @api.model
    def _timesheet_domain_get_invoiced_lines(self, *args, **kwargs):
        domain = super()._timesheet_domain_get_invoiced_lines(*args, **kwargs)

        date_from = self._context.get("timesheet_date_from")
        if date_from:
            domain = AND([domain, [('date', '>=', date_from)]])

        date_to = self._context.get("timesheet_date_to")
        if date_to:
            domain = AND([domain, [('date', '<=', date_to)]])

        return domain
