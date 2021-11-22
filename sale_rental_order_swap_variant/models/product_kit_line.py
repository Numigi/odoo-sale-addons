# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductKitLine(models.Model):
    _inherit = "product.kit.line"

    allow_change_variant = fields.Boolean()
    allow_change_product = fields.Boolean()

    @api.onchange("is_important")
    def _onchange_is_important(self):
        if self.allow_change_variant and not self.is_important:
            self.allow_change_variant = False

        if self.allow_change_product and not self.is_important:
            self.allow_change_product = False
