# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_change_variant_kit_component = fields.Boolean()

    def prepare_kit_component(self, kit_line):
        new_line = super().prepare_kit_component(kit_line)
        new_line.is_change_variant_kit_component = kit_line.is_change_variant
        return new_line

    @api.multi
    def change_variant(self, product):
        self.ensure_one()
        done_move = self.move_ids.filtered(lambda m: m.state == "done")
        if done_move:
            raise ValidationError(
                _(
                    "The variant swap can not be done since the sale order line with product {} is linked to a stock "
                    "move that is already done ({})."
                ).format(self.product_id.display_name, done_move[0].reference)
            )
        self.product_id = product
        self.product_id_change()
        self.move_ids.write({"product_id": product.id})
