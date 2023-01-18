# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def _get_domain_locations(self):
        (
            domain_quant_loc,
            domain_move_in_loc,
            domain_move_out_loc,
        ) = super()._get_domain_locations()
        if self._context.get("from_sale_order"):
            domain_quant_loc += [
                (
                    "location_id.is_rental_stock_location",
                    "=",
                    self._context.get("is_rental_sale"),
                )
            ]
        return domain_quant_loc, domain_move_in_loc, domain_move_out_loc
