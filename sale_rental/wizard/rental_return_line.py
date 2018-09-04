# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from collections import defaultdict
from odoo import api, fields, models


class RentalReturnLine(models.TransientModel):

    _name = 'rental.return.line'
    _description = 'Rental Return Wizard Line'

    wizard_id = fields.Many2one('rental.return.wizard', ondelete='cascade')

    origin_line_id = fields.Many2one('stock.move.line', 'Origin Move Line', required=True)
    origin_move_id = fields.Many2one(
        'stock.move', 'Origin Move',
        related='origin_line_id.move_id', readonly=True,
    )
    product_id = fields.Many2one(
        'product.product', 'Product',
        related='origin_line_id.product_id', readonly=True,
    )
    lot_id = fields.Many2one(
        'stock.production.lot', 'Serial Number',
        related='origin_line_id.lot_id', readonly=True,
    )

    @api.multi
    def process_rental_return(self):
        lines_by_picking = defaultdict(lambda: self.env['rental.return.line'])

        for line in self:
            lines_by_picking[line.origin_move_id.picking_id] |= line

        return_pickings = self.env['stock.picking']

        for picking, lines in lines_by_picking.items():
            origin_move_lines = lines.mapped('origin_line_id')
            return_picking = self._generate_return_picking(picking, origin_move_lines)
            self._validate_return_picking(return_picking, origin_move_lines)
            return_pickings |= return_picking

        return return_pickings

    def _generate_return_picking(self, origin_picking, origin_move_lines):
        wizard_fields = [
            'product_return_moves',
            'move_dest_exists',
            'parent_location_id',
            'original_location_id',
            'location_id',
        ]
        wizard_cls = self.env['stock.return.picking'].with_context(active_id=origin_picking.id)
        wizard_defaults = wizard_cls.default_get(wizard_fields)
        wizard = wizard_cls.create(wizard_defaults)

        for move in wizard.product_return_moves:
            origin_lines = move.move_id.move_line_ids.filtered(lambda l: l in origin_move_lines)
            move.quantity = len(origin_lines)
            move.to_refund = True

        return_picking_id = wizard.create_returns()['res_id']
        return self.env['stock.picking'].browse(return_picking_id)

    def _validate_return_picking(self, return_picking, origin_move_lines):
        for move in return_picking.move_lines:
            origin_lines = origin_move_lines.filtered(
                lambda l: l.move_id == move.origin_returned_move_id)

            for line in origin_lines:
                move.move_line_ids |= self.env['stock.move.line'].create(dict(
                    move._prepare_move_line_vals(), qty_done=1, lot_id=line.lot_id.id))

        return_picking.action_done()
