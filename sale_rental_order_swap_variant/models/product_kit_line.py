# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductKitLine(models.Model):
    _inherit = "product.kit.line"

    is_change_variant = fields.Boolean("Change Variant")

    @api.onchange("is_important")
    def _onchange_is_important(self):
        if self.is_change_variant and not self.is_important:
            self.is_change_variant = False
