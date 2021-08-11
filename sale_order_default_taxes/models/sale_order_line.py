# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _compute_tax_id(self):
        res = super()._compute_tax_id()
        for record in self:
            if record.company_id.account_sale_tax_id:
                record.tax_id = record.company_id.account_sale_tax_id
        return res
