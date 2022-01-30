# -*- coding: utf-8 -*-
from odoo import http

# class SaleOrderAvailableQtyPopoverRental(http.Controller):
#     @http.route('/sale_order_available_qty_popover_rental/sale_order_available_qty_popover_rental/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_order_available_qty_popover_rental/sale_order_available_qty_popover_rental/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_order_available_qty_popover_rental.listing', {
#             'root': '/sale_order_available_qty_popover_rental/sale_order_available_qty_popover_rental',
#             'objects': http.request.env['sale_order_available_qty_popover_rental.sale_order_available_qty_popover_rental'].search([]),
#         })

#     @http.route('/sale_order_available_qty_popover_rental/sale_order_available_qty_popover_rental/objects/<model("sale_order_available_qty_popover_rental.sale_order_available_qty_popover_rental"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_order_available_qty_popover_rental.object', {
#             'object': obj
#         })