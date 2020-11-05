# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_change_variant_kit_component = fields.Boolean()

    def prepare_kit_component(self, kit_line):
        new_line = super().prepare_kit_component(kit_line)
        new_line.is_change_variant_kit_component = kit_line.is_change_variant
        return new_line
