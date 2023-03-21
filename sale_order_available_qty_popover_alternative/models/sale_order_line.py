# © 2022 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


import logging

_logger = logging.getLogger(__name__)
ALMOST_OUT_OF_STOCK_PARAM = "sale_order_available_qty_popover.almost_out_of_stock_qty"
SO_POPOVER_ALTER_PARAM = "sale_order_available_qty_popover_alternative.so_popover_alternative"
GREEN = "#246b03"
YELLOW = "#fad817"
RED = "#ee1010"


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.depends("product_id", "product_uom_qty", "order_id.warehouse_id", "order_id.is_rental")
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
            rental_location = self.env['stock.location'].search([('is_rental_stock_location', '=', True),
                                                                 ('company_id', '=', self.company_id.id)
                                                                 ]).filtered(
                lambda l: l.get_warehouse().id == self.order_id.warehouse_id.id)
            location_ids = rental_location if self.order_id.is_rental else self.order_id.warehouse_id.lot_stock_id
            available_qty = sum(self.env['stock.quant']._get_available_quantity(
                self.product_id, loc) for loc in location_ids)
            return available_qty

    def _get_available_qty_in_all_warehouse(self):
        all_warehouses = self.env['stock.warehouse'].search([
            ('company_id', '=', self.company_id.id)
        ])
        available_qty_all = sum(self.env['stock.quant']._get_available_quantity(
            self.product_id,  w.lot_stock_id)for w in all_warehouses)
        return available_qty_all

    @api.depends("product_id", "product_uom_qty", "order_id.warehouse_id" ,"order_id.is_rental")
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
