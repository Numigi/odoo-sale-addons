# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockMoveWithRentalReturnedQuantity(models.Model):

    _inherit = 'stock.move'

    rental_returned_quantity = fields.Float(
        'Returned Quantity', compute='_compute_rental_returned_quantity',
        digits=dp.get_precision('Product Unit of Measure'))

    def _compute_rental_returned_quantity(self):
        for move in self:
            move.rental_returned_quantity = len(
                move.move_line_ids.filtered(lambda m: m.rental_state == 'returned'))


class StockMoveWithIsRentalDelivery(models.Model):

    _inherit = 'stock.move'

    is_rental_delivery = fields.Boolean('Rental Delivery', related='picking_id.is_rental_delivery')
