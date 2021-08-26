# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def action_assign_salesperson(self):
        self.ensure_one()
        return {
            "name": _("Assign Salesperson"),
            "type": "ir.actions.act_window",
            "res_model": "assign.salesperson.by.area.wizard",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
        }
