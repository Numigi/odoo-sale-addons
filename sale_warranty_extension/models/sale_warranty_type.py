# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleWarrantyType(models.Model):
    _inherit = "sale.warranty.type"

    use_warranty_extension = fields.Boolean()
    extension_duration_in_months = fields.Integer()
    extension_template_id = fields.Many2one(
        "sale.subscription.template",
        "Extension Subscription Template",
        ondelete="restrict",
    )
