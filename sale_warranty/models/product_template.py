# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = "product.template"

    warranty_type_ids = fields.Many2many(
        "sale.warranty.type",
        "product_template_warranty_type_rel",
        "product_id",
        "warranty_type_id",
        "Warranties",
    )

    @api.constrains(
        "warranty_type_ids",
        "warranty_type_ids.allow_non_serialized_products",
        "tracking",
    )
    def _check_warranties_tracking(self):
        for product in self:
            warranty_with_no_serial = product.warranty_type_ids.filtered(
                lambda w: not w.allow_non_serialized_products
            )
            is_serialized = product.tracking == "serial"
            if warranty_with_no_serial and not is_serialized:
                raise ValidationError(
                    _(
                        "The warranty {warranty} does not allow products "
                        "that are not tracked with a serial number."
                        "\n(Product: {product})"
                    ).format(
                        warranty=warranty_with_no_serial[0].display_name,
                        product=product.display_name,
                    )
                )
