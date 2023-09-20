# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_popup_color = fields.Char(compute='_compute_qty_popup_color')
    free_qty = fields.Float(related='product_id.free_qty')
    qty_available = fields.Float(related='product_id.qty_available')
    virtual_available = fields.Float(related='product_id.virtual_available')
    outgoing_qty = fields.Float(related='product_id.outgoing_qty')

    @api.depends('qty_available_today', 'free_qty_today', 'product_uom_qty', 'order_id.state', 'virtual_available_at_date')
    def _compute_qty_popup_color(self):
        for rec in self:

            if rec.state in ('draft', 'sent'):
                if rec.virtual_available_at_date >= rec.product_uom_qty:
                    rec.qty_popup_color = "text-primary"

                elif 0 < rec.virtual_available_at_date < rec.product_uom_qty:
                    rec.qty_popup_color = "text-warning"
                else:
                    rec.qty_popup_color = "text-danger"

            elif rec.state == 'sale':
                qty = rec.free_qty

                if qty <= 0:
                    rec.qty_popup_color = "text-danger"
                else:
                    rec.qty_popup_color = "text-primary"
            else:
                # The else statement is not used in the widget
                # Used to prevent bugs related to a miss computing of all states ( depends on odoo version)
                rec.qty_popup_color = "text-danger"

