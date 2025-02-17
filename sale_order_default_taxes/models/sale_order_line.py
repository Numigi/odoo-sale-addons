# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_tax_id(self):
        res = super()._compute_tax_id()
        for record in self.filtered(lambda r: not r.tax_id):
            if record.company_id.account_sale_tax_id:
                record.tax_id = record.company_id.account_sale_tax_id
        return res
