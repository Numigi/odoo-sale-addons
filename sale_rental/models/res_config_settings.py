# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models

from .product_product import FILTER_PRODUCTS_ON_ORDERS


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    rental_buffer = fields.Integer(related="company_id.rental_buffer", readonly=False)
    rental_filter_products_on_orders = fields.Boolean(
        string="Filter Rental Products on Sales Orders",
        config_parameter=FILTER_PRODUCTS_ON_ORDERS,
    )
