# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class ProductProduct__enhanced_availability(models.Model):
    _inherit = "product.product"

    replenishment_delay = fields.Integer()
    replenishment_availability = fields.Float(
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
    )
    sale_availability = fields.Float(
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
    )

    def compute_availability(self):
        for product in self:
            sale_availability = product._get_sale_availability()
            next_replenishment_qty = product._get_next_replenishment_quantity()
            product.sale_availability = sale_availability
            product.replenishment_availability = (
                sale_availability + next_replenishment_qty
            )

    def _get_sale_availability(self):
        current_qty = self.__get_current_qty()
        out_qty = self.__get_outgoing_qty()
        return current_qty - out_qty

    def _get_next_replenishment_quantity(self):
        picking = self.__get_next_receipt()
        moves = picking.mapped("move_lines").filtered(lambda m: m.product_id == self)
        return sum(m.product_qty for m in moves)

    def _set_enhanced_availability_info(self, info, add_qty):
        if self.__show_availability():
            self.__set_availability(info, add_qty)

    def __set_availability(self, info, add_qty):
        info["show_availability"] = True

        if self.__show_available_qty():
            info["show_available_qty"] = True

        elif self.__show_available_qty_warning(add_qty):
            info["show_available_qty_warning"] = True

        elif self.__show_in_stock(add_qty):
            info["show_in_stock"] = True

        elif self.__show_replenishment_delay(add_qty):
            info["show_replenishment_delay"] = True
            info["replenishment_delay_message"] = self.__get_replenishment_message()

    def __show_availability(self):
        return self.inventory_availability not in ("never", "custom")

    def __show_available_qty(self):
        return self.inventory_availability == "always"

    def __show_available_qty_warning(self, add_qty):
        is_threshold = self.inventory_availability in ("threshold", "threshold_warning")
        qty_below_threshold = self.sale_availability <= self.available_threshold
        enough_available = add_qty <= self.sale_availability
        return is_threshold and qty_below_threshold and enough_available

    def __show_in_stock(self, add_qty):
        return self.sale_availability >= add_qty

    def __show_replenishment_delay(self, add_qty):
        return self.replenishment_availability >= add_qty

    def __get_replenishment_message(self):
        return _(
            "Unfortunately, the stock level is currently low for this product. "
            "We estimate a better availability of this product in a delay of "
            "{} days."
        ).format(self.replenishment_delay)

    def __get_next_receipt(self):
        domain = [
            *self.__get_pending_stock_move_domain(),
            ("location_dest_id.usage", "=", "internal"),
            ("location_id.usage", "=", "supplier"),
        ]
        move = self.env["stock.move"].search(domain, limit=1)
        return move.picking_id

    def __get_current_qty(self):
        domain = [
            ("product_id", "=", self.id),
            ("location_id.usage", "=", "internal"),
        ]
        field = "quantity"
        res = self.env["stock.quant"].read_group(domain, [field], [field])
        return res[0][field] if res else 0

    def __get_outgoing_qty(self):
        domain = [
            *self.__get_pending_stock_move_domain(),
            ("location_dest_id.usage", "=", "customer"),
            ("location_id.usage", "=", "internal"),
        ]
        field = "product_qty"
        res = self.env["stock.move"].read_group(domain, [field], [field])
        return res[0][field] if res else 0

    def __get_pending_stock_move_domain(self):
        return [
            ("product_id", "=", self.id),
            ("state", "not in", ("done", "cancel", "done")),
        ]
