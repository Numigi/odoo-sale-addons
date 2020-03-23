# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    is_rental = fields.Boolean("Rental")

    def get_rental_customer_location(self):
        return self.env.ref("sale_rental.customer_location")

    @api.multi
    def action_confirm(self):
        super().action_confirm()
        rental_orders = self.filtered(lambda l: l.is_rental)
        for line in rental_orders.mapped("order_line"):
            line.propagate_stock_rental_dates()
        return True

    @api.model
    def create(self, vals):
        order = super().create(vals)
        order.propagate_service_rental_dates()
        return order

    def propagate_service_rental_dates(self):
        for line in self.mapped("order_line").filtered(lambda l: l.is_rental_service):
            line.propagate_service_rental_dates()
