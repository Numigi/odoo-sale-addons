# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class WarrantyType(models.Model):

    _name = "sale.warranty.type"
    _description = "Sale Warranty Type"

    company_id = fields.Many2one(
        "res.company", "Company", default=lambda s: s.env.user.company_id
    )
    name = fields.Char(required=True)
    duration_in_months = fields.Integer(required=True)
    description = fields.Text()
    url = fields.Char(string="URL")
    allow_non_serialized_products = fields.Boolean(
        help="If checked, this warranty type is selectable on non-serialized products."
    )
    product_template_ids = fields.Many2many(
        "product.template",
        "product_template_warranty_type_rel",
        "warranty_type_id",
        "product_id",
        "Products",
    )
    active = fields.Boolean(default=True)

    def write(self, vals):
        super().write(vals)
        if "allow_non_serialized_products" in vals:
            self.mapped("product_template_ids")._check_warranties_tracking()
        return True
