# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    target_margin_min = fields.Float(
        string="Min. Target Margin",
        help="Allows you to set a minimum and maximum target margin for "
             "the sale of items in this category. \n If the margin % on "
             "the sale order lines is below the minimum margin, "
             "it is displayed in red. \n If it is within the defined range,"
             " it is displayed in yellow. \n If it exceeds "
             "the maximum margin, it is displayed in green."
    )
    target_margin_max = fields.Float(
        string="Max. Target Margin"
    )

    @api.constrains('target_margin_min', 'target_margin_max')
    def _check_target_margin(self):
        for record in self:
            if record.target_margin_min > record.target_margin_max:
                raise ValidationError(_('The set minimum margin must be lower '
                                        'than the set maximum margin.'))
