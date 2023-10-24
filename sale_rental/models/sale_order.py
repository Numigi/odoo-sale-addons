# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    is_rental = fields.Boolean("Rental")

    def get_rental_customer_location(self):
        return self.env.ref("stock_rental.customer_location")

    def action_confirm(self):
        super().action_confirm()
        rental_orders = self.filtered(lambda l: l.is_rental)
        for line in rental_orders.mapped("order_line"):
            line.propagate_stock_rental_dates()
        return True

    @api.model
    def create(self, vals):
        order = super().create(vals)
        order.propagate_service_rental_dates()
        return order

    def propagate_service_rental_dates(self):
        for line in self.mapped("order_line").filtered(lambda l: l.is_rental_service):
            line.propagate_service_rental_dates()


class SaleOrderWithReturnedQty(models.Model):

    _inherit = "sale.order"

    rental_returned_qty_invisible = fields.Boolean(
        compute="_compute_rental_returned_qty_invisible"
    )

    def _compute_rental_returned_qty_invisible(self):
        for order in self:
            order.rental_returned_qty_invisible = (
                not order.is_rental or order.state not in ("sale", "done")
            )


class SaleOrderWithExtraSmartButton(models.Model):

    _inherit = "sale.order"

    rental_return_count = fields.Integer(compute="_compute_picking_ids")

    def _compute_picking_ids(self):
        super()._compute_picking_ids()
        for order in self:
            return_pickings = self._get_rental_return_pickings()
            order.delivery_count -= len(return_pickings)
            order.rental_return_count = len(return_pickings)

    def _get_rental_return_pickings(self):
        return self.mapped("picking_ids").filtered(_is_rental_return_picking)

    def action_view_delivery(self):
        if self.is_rental:
            return self._action_view_rental_delivery()
        return super().action_view_delivery()

    def _action_view_rental_delivery(self):
        pickings = self.mapped("picking_ids") - \
            self._get_rental_return_pickings()
        return self._get_picking_list_action(pickings)

    def action_view_rental_return_pickings(self):
        pickings = self._get_rental_return_pickings()
        return self._get_picking_list_action(pickings)

    def _get_picking_list_action(self, pickings):
        # using self.env['ir.actions.act_window'] could be the same
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all")
        action["domain"] = [("id", "in", pickings.ids)]
        return action


def _is_rental_return_picking(picking):
    origin_moves = _get_move_with_origin_moves(picking.move_lines)
    return any(m for m in origin_moves if m.is_rental_return_move())


def _get_move_with_origin_moves(moves, depth=10):
    origin_moves = moves.mapped("move_orig_ids")
    return (
        moves | _get_move_with_origin_moves(origin_moves, depth - 1)
        if origin_moves and depth > 0
        else moves
    )
