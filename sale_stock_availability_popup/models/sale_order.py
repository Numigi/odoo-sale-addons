# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
import logging

logger = logging.getLogger(__name__)



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_popup_color = fields.Char(compute='_compute_qty_popup_color')
    free_qty = fields.Float(related='product_id.free_qty')
    qty_available = fields.Float(related='product_id.qty_available')
    virtual_available = fields.Float(related='product_id.virtual_available')
    outgoing_qty = fields.Float(related='product_id.outgoing_qty')
    reserved_qty = fields.Float(compute="_get_reserved_qty", store=False)
    available_qty = fields.Float(compute="_get_reserved_qty", store=False)

    @api.depends("order_id", "product_id")
    def _get_reserved_qty(self):
        for rec in self:
            domain = [("product_id", "=", rec.product_id.id),
                      ("state", "in", ["partially_available", "assigned"])]
            stock_move_out_ids = self.env['stock.move'].search(domain)
            reserved_qty = 0
            for move in stock_move_out_ids:
                reserved_qty = reserved_qty + move.reserved_availability
            rec.reserved_qty = reserved_qty
            rec.available_qty = rec.qty_available - reserved_qty

    @api.depends('reserved_qty', 'qty_available', 'product_uom_qty', 'product_id')
    def _compute_qty_popup_color(self):
        for rec in self:
            if rec.order_id.state == 'sale':
                if rec.available_qty > 0:
                    rec.qty_popup_color = 'text-success'
                elif 0 < rec.free_qty_today < rec.product_uom_qty:
                    rec.qty_popup_color = 'text-warning'
                else:
                    rec.qty_popup_color = 'text-danger'
            else:
                if rec.qty_available - rec.reserved_qty >= rec.product_uom_qty:
                    rec.qty_popup_color = 'text-success'
                elif 0 < rec.free_qty_today < rec.product_uom_qty:
                    rec.qty_popup_color = 'text-warning'
                else:
                    rec.qty_popup_color = 'text-danger'

