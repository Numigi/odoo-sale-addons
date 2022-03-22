# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.osv.expression import AND


class SaleOrderLine__timesheet_invoicing_period(models.Model):

    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, qty):
        date_from = self._context.get("timesheet_date_from")
        date_to = self._context.get("timesheet_date_to")

        if (date_from or date_to) and self.qty_delivered_method == "timesheet":
            qty = self.__get_qty_to_invoice()

        return super()._prepare_invoice_line(qty)

    def __get_qty_to_invoice(self):
        domain = self.env["account.invoice.line"]._timesheet_domain_get_invoiced_lines(self)
        lines = self.env["account.analytic.line"].search(domain)
        return sum(l.unit_amount for l in lines)
