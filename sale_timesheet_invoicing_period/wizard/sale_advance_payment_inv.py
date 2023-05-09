# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = "sale.advance.payment.inv"

    timesheet_date_from = fields.Date()
    timesheet_date_to = fields.Date()

    def create_invoices(self):
        self = self.with_context(
            timesheet_date_from=self.timesheet_date_from,
            timesheet_date_to=self.timesheet_date_to,
        )
        return super(SaleAdvancePaymentInv, self).create_invoices()
