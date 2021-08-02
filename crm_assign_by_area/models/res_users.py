# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.multi
    def name_get(self):
        context_territory_ids = self._context.get(
            "assign_salesperson_by_area_territory_ids", {}
        )
        if context_territory_ids:
            result = []
            territories = self.env["res.territory"].browse(context_territory_ids[0][2])
            for territory in territories:
                salesperson = territory.salesperson_id
                result.append(
                    (
                        salesperson.id,
                        "{} ({})".format(salesperson.name, territory.display_name),
                    )
                )
            return result
        else:
            return super().name_get()
