# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    whole_order_invoiced = fields.Boolean(copy=False)

    @api.depends(
        'state', 'order_line.invoice_status', 'order_line.invoice_lines',
        'whole_order_invoiced')
    def _get_invoiced(self):
        super()._get_invoiced()
        invoiced_orders = self.filtered(lambda o: o.whole_order_invoiced)
        invoiced_orders.update({'invoice_status': 'invoiced'})


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.depends(
        'state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced',
        'order_id.whole_order_invoiced')
    def _compute_invoice_status(self):
        super()._compute_invoice_status()
        invoiced_lines = self.filtered(lambda l: l.order_id.whole_order_invoiced)
        invoiced_lines.update({'invoice_status': 'invoiced'})
