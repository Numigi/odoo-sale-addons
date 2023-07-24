# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    select_lines = fields.Boolean(
        compute="_compute_select_lines",
        inverse="_inverse_select_lines",
        string="Select lines",
        help="Check this box to select all sale order lines.",
    )

    @api.depends('order_line', 'order_line.select_line')
    def _compute_select_lines(self):
        for so in self:
            so.select_lines = True if all(line.select_line is True for line in so.order_line) else False

    def _inverse_select_lines(self):
        for so in self:
            if so.select_lines:
                so.order_line.write({
                    'select_line': True,
                })
            else:
                False
