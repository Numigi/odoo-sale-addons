# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    select_lines = fields.Boolean(
        compute="_compute_select_lines",
        string="Select lines",
        help="Check this box to select all sale order lines.",
        readonly=False,
        store=False,
    )

    @api.onchange("select_lines", "order_line")
    def _onchange_select_lines(self):
        if self.select_lines:
            self.order_line.select_line = True
        if not self.select_lines and all(
            line.select_line is True for line in self.order_line
        ):
            self.order_line.select_line = False

    @api.onchange("order_line")
    def _onchange_order_line(self):
        self._compute_select_lines()

    def _compute_select_lines(self):
        for so in self:
            if all(line.select_line is True for line in so.order_line):
                so.select_lines = True
            else:
                so.select_lines = False
