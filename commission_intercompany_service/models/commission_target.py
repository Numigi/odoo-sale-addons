# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class CommissionTarget(models.Model):

    _inherit = "commission.target"

    def _get_related_sale_order(self, invoice_line):
        orders = super()._get_related_sale_order(invoice_line)
        interco_orders = invoice_line.mapped("invoice_id.interco_service_order_id")
        return orders | interco_orders
