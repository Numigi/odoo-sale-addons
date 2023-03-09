# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    def name_get(self):
        territories = self._get_territories_from_context()
        if territories:
            return [
                (user.id, user._get_name_with_territories(territories)) for user in self
            ]
        else:
            return super().name_get()

    def _get_territories_from_context(self):
        context_territory_ids = self._context.get(
            "assign_salesperson_by_area_territory_ids"
        )
        if context_territory_ids:
            return self.env["res.territory"].browse(context_territory_ids[0][2])
        else:
            return None

    def _get_name_with_territories(self, territories):
        user_territories = territories.filtered(lambda r: r.salesperson_id == self)
        return "{} ({})".format(
            self.name, ", ".join(user_territories.mapped("display_name"))
        )
