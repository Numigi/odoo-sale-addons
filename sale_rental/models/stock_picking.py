# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingWithOpenRentalReturnWizard(models.Model):
    """Add an action to open a rental return wizard."""

    _inherit = 'stock.picking'

    def open_rental_return_wizard(self):
        returnable_lines = self.move_line_ids.filtered(
            lambda l: l.move_id.sale_line_id.is_rented_product and not l.rental_return_id)

        wizard = self.env['rental.return.wizard'].create({})

        for line in returnable_lines:
            wizard.line_ids |= self.env['rental.return.line'].create({'origin_line_id': line.id})

        action = wizard.get_formview_action()
        action['target'] = 'new'
        return action


class StockPickingWithIsRentalDelivery(models.Model):
    """Add a computed boolean field to identify rental deliveries."""

    _inherit = 'stock.picking'

    is_rental_delivery = fields.Boolean('Rental Delivery', compute='_compute_is_rental_delivery')

    def _compute_is_rental_delivery(self):
        for picking in self:
            picking.is_rental_delivery = (
                picking.sale_id.type_id.is_rental and
                picking.location_dest_id.usage == 'customer'
            )
