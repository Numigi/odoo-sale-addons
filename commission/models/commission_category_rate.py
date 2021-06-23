# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class CommissionCategoryRate(models.Model):
    _name = "commission.category.rate"
    _description = "Commission Category Rate"

    category_id = fields.Many2one("commission.category", required=True)
    slice_from = fields.Float(required=True)
    slice_to = fields.Float(required=True)
    commission_percentage = fields.Float(required=True)

    @api.constrains("slice_from", "slice_to")
    def _validate_slices(self):
        if self.slice_to < self.slice_from:
            raise ValidationError(
                "The upper bound should be greater than the lower bound."
            )
