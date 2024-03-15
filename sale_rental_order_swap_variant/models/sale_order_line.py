# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    allow_change_product = fields.Boolean()
    allow_change_variant = fields.Boolean()
    change_variant_button_visible = fields.Boolean(
        compute="_compute_change_variant_button_visible"
    )

    @api.depends(
        "allow_change_variant",
        "allow_change_product",
    )
    def _compute_change_variant_button_visible(self):
        for line in self:
            line.change_variant_button_visible = line.order_id.state not in (
                "done",
                "cancel",
            ) and (line.allow_change_variant or line.allow_change_product)

    def prepare_kit_component(self, kit_line):
        new_line = super().prepare_kit_component(kit_line)
        new_line.allow_change_variant = kit_line.allow_change_variant
        new_line.allow_change_product = kit_line.allow_change_product
        return new_line

    def change_variant(self, product, quantity):
        self._post_change_variant_message(product, quantity)

        self._check_no_done_stock_move()
        self._cancel_all_stock_moves()
        self.product_id = product
        product_with_lang = product.with_context(lang=self.order_id.partner_id.lang)
        self.name = self.get_sale_order_line_multiline_description_sale(
            product_with_lang
        )
        self.product_uom_qty = quantity

        self._action_launch_stock_rule()

    def _post_change_variant_message(self, product, quantity):
        if self.product_id == product:
            product_line = _("{} (unchanged)").format(product.display_name)
        else:
            product_line = f"{self.product_id.display_name} --> {product.display_name}"

        if quantity == self.product_uom_qty:
            quantity_line = _("{} (unchanged)").format(quantity)
        else:
            quantity_line = f"{self.product_uom_qty} --> {quantity}"

        body = _(
            """
            Important component changed on a kit
            <ul>
                <li>Product: {}</li>
                <li>Quantity: {}</li>
            </ul>
            """
        ).format(product_line, quantity_line)

        self.order_id.message_post(body=body)

    def _cancel_all_stock_moves(self):
        self._cancel_push_stock_moves()
        self._cancel_pull_stock_moves()

    def _cancel_push_stock_moves(self):
        moves = self.move_ids.mapped("move_dest_ids")
        limit = 10
        while moves and limit:
            dest_moves = moves.mapped("move_dest_ids")
            _cancel_stock_moves(moves)
            moves = dest_moves
            limit -= 1

    def _cancel_pull_stock_moves(self):
        moves = self.move_ids
        limit = 10
        while moves and limit:
            orig_moves = moves.mapped("move_orig_ids")
            _cancel_stock_moves(moves)
            moves = orig_moves
            limit -= 1

    def _check_no_done_stock_move(self):
        done_move = _with_all_origin_moves(self.move_ids).filtered(
            lambda m: m.is_done_move()
        )
        if done_move:
            raise ValidationError(
                _(
                    "The variant swap can not be done since the sale order line "
                    "with product {} is linked to a stock move that is already done ({})."
                ).format(self.product_id.display_name, done_move[0].reference)
            )


def _with_all_origin_moves(stock_move):
    origin_moves = stock_move.mapped("move_orig_ids")
    if not origin_moves:
        return stock_move
    return stock_move | _with_all_origin_moves(origin_moves)


def _cancel_stock_moves(moves):
    moves._action_cancel()
    moves.write({"picking_id": False})
