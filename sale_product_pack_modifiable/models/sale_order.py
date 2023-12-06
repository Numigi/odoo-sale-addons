# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self, vals):
        if "order_line" in vals:
            to_delete_ids = [e[1] for e in vals["order_line"] if e[0] == 2]

            # Recompute main parent price unit if some child was removed
            line_removed_ids = self.env["sale.order.line"].search(
                [("id", "in", to_delete_ids)]
            )
            for line in line_removed_ids:
                main_parent = self.env["sale.order.line"].search(
                    [("id", "parent_of", line.id)], limit=1
                )

                # Divide by main_parent.product_uom_qty because initial quantities on
                # product_id.pack_line_ids may be multiplied if the price unit of main parent pack
                # was changed

                # For line which is not a pack
                if not line.product_id.pack_ok:
                    new_price_unit = main_parent.price_unit - (
                        line.product_id.list_price
                        * line.product_uom_qty
                        / main_parent.product_uom_qty
                    )
                    main_parent.price_unit = new_price_unit
                else:
                    # In case it's a pack so it may contain some child lines
                    if line.pack_child_line_ids:
                        # we compute with pack_child_line_ids instead of product_id.pack_line_ids
                        # to handle case if some child line is previously removed
                        # avoid using lst_price on pack
                        pack_price_left = 0
                        for pack_child_line in line.pack_child_line_ids:
                            pack_price_left += (
                                pack_child_line.product_uom_qty
                                / main_parent.product_uom_qty
                            ) * pack_child_line.product_id.product_tmpl_id.lst_price
                        new_price_unit = main_parent.price_unit - pack_price_left
                        main_parent.price_unit = new_price_unit

        return super().write(vals)
