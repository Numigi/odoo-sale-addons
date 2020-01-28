# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    margin_percent = fields.Float(
        string='Margin Percentage',
        compute='_compute_margin_percent',
        store=True,
    )

    @api.depends('margin', 'price_subtotal')
    def _compute_margin_percent(self):
        for line in self:
            line.margin_percent = (
                line.margin / line.price_subtotal
                if line.price_subtotal else None
            )
