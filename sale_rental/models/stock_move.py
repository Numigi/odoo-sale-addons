# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.addons.stock.models.stock_move import StockMove


class StockMoveLineWithIsRentalReturn(models.Model):

    _inherit = 'stock.move.line'

    is_rental_return = fields.Boolean(
        'Is Rental Return', compute='_compute_is_rental_return', store=True)

    @api.depends('move_id', 'location_id', 'location_dest_id')
    def _compute_is_rental_return(self):
        for line in self:
            line.is_rental_return = (
                line.move_id.sale_line_id.is_rented_product and
                line.location_id.usage == 'customer' and
                line.location_dest_id.usage != 'customer'
            )


class StockMoveLineWithLinkBetweenRentedProducts(models.Model):

    _inherit = 'stock.move.line'

    rental_return_id = fields.Many2one(
        'stock.move.line', 'Rental Return', ondelete='restrict', index=True)

    def _action_done(self):
        super()._action_done()

        rental_return_lines = self.filtered(lambda l: l.exists() and l.is_rental_return)

        for line in rental_return_lines:
            line._link_to_origin_rental_delivery_line()

    def _link_to_origin_rental_delivery_line(self):
        origin_line = self.move_id.move_orig_ids.move_line_ids.filtered(
            lambda l: l.lot_id == self.lot_id)
        origin_line.rental_return_id = self


class StockMoveLineWithRentalReturnDate(models.Model):

    _inherit = 'stock.move.line'

    rental_date_to = fields.Date(
        'Expected Return Date', compute='_compute_rental_date_to', store=True)

    @api.depends('move_id', 'rental_return_id.date')
    def _compute_rental_date_to(self):
        for line in self:
            expected_return_date = (
                line.rental_return_id.date or
                line.move_id.sale_line_id.rental_date_to
            )
            line.rental_date_to = max(expected_return_date, line.date)


class StockMoveLineWithRentalState(models.Model):
    """Add the rental state to stock move lines.

    The rental state is the same as the state of the move, but with one extra
    state to indicate that the item has been returned.
    """

    _inherit = 'stock.move.line'

    rental_state = fields.Selection(
        [
            ('draft', 'New'),
            ('cancel', 'Cancelled'),
            ('waiting', 'Waiting Another Move'),
            ('confirmed', 'Waiting Availability'),
            ('partially_available', 'Partially Available'),
            ('assigned', 'Available'),
            ('done', 'Done'),
            ('returned', 'Returned'),
        ],
        'Rental State', compute='_compute_rental_state', store=True
    )

    @api.depends('state', 'rental_return_id')
    def _compute_rental_state(self):
        for line in self:
            line.rental_state = 'returned' if line.rental_return_id.state == 'done' else line.state
