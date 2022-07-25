# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.osv.expression import AND

FILTER_PRODUCTS_ON_ORDERS = "sale_rental.filter_products_on_orders"


class Product(models.Model):

    _inherit = "product.product"

    rented_product_ids = fields.One2many(
        "product.template", "rental_service_id", "Rented Products"
    )

    @api.onchange("can_be_rented")
    def _if_can_be_rented__then_sale_ok(self):
        if self.can_be_rented:
            self.sale_ok = True

    @api.constrains("uom_id")
    def _check_rental_service_is_in_days(self):
        self.mapped("rented_product_ids")._check_rental_service_is_in_days()

    @api.model
    def _search(self, args, *args_, **kwargs):
        if _should_filter_on_sales_orders(self.env):
            if self._context.get("is_rental_sale_order"):
                args = AND([args or [], [("can_be_rented", "=", True)]])
        return super()._search(args, *args_, **kwargs)


def _should_filter_on_sales_orders(env):
    value = env["ir.config_parameter"].sudo().get_param(FILTER_PRODUCTS_ON_ORDERS)
    return value == "True"
