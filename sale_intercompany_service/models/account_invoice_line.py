# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    interco_service_type = fields.Selection(related="invoice_id.interco_service_type")

    def get_invoice_line_account(self, type, product, fpos, company):
        if self.interco_service_type == "interco_customer":
            account = product.categ_id.intercompany_revenue_account_id
            if account:
                return account
        
        if self.interco_service_type == "interco_supplier":
            account = product.categ_id.intercompany_expense_account_id
            if account:
                return account
        
        return super().get_invoice_line_account(type, product, fpos, company)
