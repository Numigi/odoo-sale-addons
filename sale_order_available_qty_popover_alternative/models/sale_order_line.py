# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


ALMOST_OUT_OF_STOCK_PARAM = "sale_order_available_qty_popover.almost_out_of_stock_qty"
SO_POPOVER_ALTER_PARAM = "sale_order_available_qty_popover_alternative.so_popover_alternative"
GREEN = "#246b03"
YELLOW = "#fad817"
RED = "#ee1010"


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.depends("product_id", "product_uom_qty", "order_id.warehouse_id")
    def _compute_available_qty_for_popover(self):
        so_popover_alternative = self.env[
            'ir.config_parameter'].sudo().get_param(
            SO_POPOVER_ALTER_PARAM, False)
        if so_popover_alternative:
            for line in self:
                line.available_qty_for_popover = \
                    line._get_available_qty_for_popover_alt()
        else:
            super(SaleOrderLine, self)._compute_available_qty_for_popover()

    def _get_reserved_quantity(self, location):
        try:
            return self.env['stock.quant']._gather(
                self.product_id,
                location,
                strict=True
            ).reserved_quantity
        except Exception:
            return 0.0



    def _get_available_qty_for_popover_alt(self):
        self.ensure_one()
        if self.product_id:
            res = self.product_id.with_context(
                    from_sale_order=True,
                    is_rental_sale=self.order_id.is_rental,
                    warehouse=self.order_id.warehouse_id.id,
                )._compute_quantities_dict(
                    self._context.get("lot_id"),
                    self._context.get("owner_id"),
                    self._context.get("package_id"),
                    self._context.get("from_date"),
                    self._context.get("to_date"),
            )
            warehouse_location = self.order_id.warehouse_id.lot_stock_id
            return res.get(self.product_id.id).get("qty_available") - \
                self._get_reserved_quantity(warehouse_location)

    def _get_available_qty_in_all_warehouse(self):
        all_warehouses = self.env['stock.warehouse'].search([
            ('company_id', '=', self.company_id.id)
        ])
        on_hand_qty = \
            self.product_id.qty_available
        reserved_qty = sum(self._get_reserved_quantity(w.lot_stock_id)
                           for w in all_warehouses)
        return on_hand_qty - reserved_qty

    @api.depends("product_id", "product_uom_qty", "order_id.warehouse_id")
    def _compute_available_qty_popover_color(self):
        so_popover_alternative = self.env['ir.config_parameter'].sudo().get_param(
            SO_POPOVER_ALTER_PARAM, False)
        if so_popover_alternative:
            self._compute_color_alt()
        else:
            super(SaleOrderLine, self)._compute_available_qty_popover_color()

    def _compute_color_alt(self):
        for line in self:
            if line.product_id:
                if line.available_qty_for_popover >= line.product_uom_qty:
                    line.available_qty_popover_color = GREEN
                elif line._get_available_qty_in_all_warehouse() >= \
                        line.product_uom_qty:
                    line.available_qty_popover_color = YELLOW
                else:
                    line.available_qty_popover_color = RED
