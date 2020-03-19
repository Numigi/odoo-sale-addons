# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = "product.template"

    can_be_rented = fields.Boolean()
    rental_service_id = fields.Many2one("product.product")

    @api.constrains("uom_id")
    def _on_uom_changed__check_rental_service_uom(self):
        self.mapped(
            "product_variant_ids.rented_product_ids"
        )._check_rental_service_is_in_days()

    @api.constrains("rental_service_id")
    def _check_rental_service_is_in_days(self):
        rental_services = self.mapped("rental_service_id")
        days = self.env.ref("uom.product_uom_day")

        for product in rental_services:
            if product.uom_id != days:
                raise ValidationError(
                    _(
                        "The rental service {} must have the unit of measure day(s)."
                    ).format(product.display_name)
                )
