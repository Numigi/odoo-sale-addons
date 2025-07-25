# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    select_line = fields.Boolean(
        string='Select line',
        help="Check this box to show the sale order line in Aeroo Reports."
    )
