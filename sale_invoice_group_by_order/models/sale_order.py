# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        grouped_by_so_number = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_invoice_create_group_by_origin.config")
        )

        if grouped_by_so_number == "on":
            super()._create_invoices(grouped=True, final=final, date=date)
        else:
            super()._create_invoices(grouped=grouped, final=final, date=date)
