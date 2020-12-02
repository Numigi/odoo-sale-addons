# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    inventory_availability = fields.Selection(
        selection_add=[
            (
                "threshold_warning",
                "Indicate if the inventory is below a threshold and allow sales if not enough stock",
            ),
            # TODO in v13+ to place more appropriately the new option : ('custom', )
        ]
    )
