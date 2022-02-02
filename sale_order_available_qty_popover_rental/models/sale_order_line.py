from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_available_qty_for_popover(self):
        if self.order_id.is_rental:
            rental_location_ids = self.env['stock.location'].search([('usage', '=', 'internal'),
                                                                     ('is_rental_stock_location', '=', True)])
            return sum(
                [quant.quantity for quant in self.env['stock.quant'].search([('product_id', '=', self.product_id.id)
                                                                                , ('location_id', 'in',
                                                                                   rental_location_ids.ids)])])
        else:
            stock_location_ids = self.env['stock.location'].search([('usage', '=', 'internal'),
                                                                    ('is_rental_stock_location', '=', False),
                                                                    ('is_rental_customer_location', '=', False)])
            return sum([quant.quantity for quant in self.env['stock.quant'].search(
                [('product_id', '=', self.product_id.id), ('location_id', 'in', stock_location_ids.ids)])])
