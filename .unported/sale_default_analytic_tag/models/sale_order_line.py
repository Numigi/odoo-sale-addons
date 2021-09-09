# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def product_id_change(self):
        super().product_id_change()

        if self.product_id:
            self.analytic_tag_ids = self.product_id.sale_analytic_tag_ids
