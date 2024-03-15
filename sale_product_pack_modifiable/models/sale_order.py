# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_round
from odoo.tools.misc import get_lang


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
                super_parent = self.env["sale.order.line"].search(
                    [("id", "parent_of", line.id)], limit=1
                )
                main_parent = (
                    super_parent
                    if (super_parent.pack_component_price == "totalized")
                    else (line.pack_parent_line_id)
                )

                # Divide by main_parent.product_uom_qty because initial
                # quantities on product_id.pack_line_ids may be multiplied
                # if the price unit of main parent pack was changed

                if main_parent.pack_component_price == "totalized":
                    new_price_unit = main_parent.price_unit
                    # For line which is not a pack
                    if not line.product_id.pack_ok:
                        new_price_unit = main_parent.price_unit - (
                            self._get_product_taxed_price(line)
                            * line.product_uom_qty
                            / main_parent.product_uom_qty
                        )
                    else:
                        # In case it's a pack so it may contain some child lines
                        if line.pack_child_line_ids:
                            # we compute with pack_child_line_ids instead of
                            # product_id.pack_line_ids to handle case if some child
                            # line is previously removed avoid using lst_price on pack.
                            pack_price_left = 0
                            for pack_child_line in line.pack_child_line_ids:
                                pack_price_left += (
                                    pack_child_line.product_uom_qty
                                    / main_parent.product_uom_qty
                                ) * self._get_product_taxed_price(
                                    pack_child_line, is_pack=True
                                )
                            new_price_unit = main_parent.price_unit - pack_price_left
                    main_parent.price_unit = float_round(
                        new_price_unit, precision_digits=2
                    )
        return super().write(vals)

    def _convert_price_unit(self, price):
        return price * self.currency_rate

    def _get_product_taxed_price(self, order_line, is_pack=False):
        """
        Send on context all information needed to compute for price.
        Then, get the price unit with all sale parameter included :

        """
        lang = get_lang(self.env, order_line.order_id.partner_id.lang).code

        order_line._compute_tax_id()

        product = order_line.product_id.with_context(
            lang=lang,
            partner=order_line.order_id.partner_id,
            quantity=order_line.product_uom_qty,
            date=order_line.order_id.date_order,
            pricelist=order_line.order_id.pricelist_id.id,
            uom=order_line.product_uom.id,
        )
        if order_line.order_id.pricelist_id and order_line.order_id.partner_id:
            unit_price = product._get_tax_included_unit_price(
                order_line.company_id,
                order_line.order_id.currency_id,
                order_line.order_id.date_order,
                "sale",
                fiscal_position=order_line.order_id.fiscal_position_id,
                product_price_unit=order_line._get_display_price(product),
                product_currency=order_line.order_id.currency_id,
            )
        else:
            # Not using pricelist, so just convert if needed
            unit_price = (
                order_line.order_id.currency_id._convert(
                    order_line.product_id.product_tmpl_id.lst_price,
                    order_line.order_id.currency_id,
                    order_line.company_id,
                    order_line.order_id.date_order,
                )
                if is_pack
                else order_line.order_id.currency_id._convert(
                    order_line.product_id.list_price,
                    order_line.order_id.currency_id,
                    order_line.company_id,
                    order_line.order_id.date_order,
                )
            )

        return unit_price
