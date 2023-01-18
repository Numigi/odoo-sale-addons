# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    warranty_ids = fields.One2many(
        'sale.warranty',
        'sale_order_id',
        'Warranties',
    )

    warranty_count = fields.Integer(
        compute='_compute_warranty_count'
    )

    def _compute_warranty_count(self):
        for order in self:
            warranties_not_cancelled = order.warranty_ids.filtered(lambda w: w.state != 'cancelled')
            order.warranty_count = len(warranties_not_cancelled)

    def action_cancel(self):
        result = super().action_cancel()
        self.sudo().mapped('warranty_ids').action_cancel()
        return result
