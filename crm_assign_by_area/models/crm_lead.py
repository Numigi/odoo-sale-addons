# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.multi
    def action_assign_salesperson(self):
        self.ensure_one()
        if not self.partner_id:
            raise ValidationError(_("Please select a customer to assign salesperson."))
        return {
            "name": _("Assign Salesperson"),
            "type": "ir.actions.act_window",
            "res_model": "assign.salesperson.by.area.wizard",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
        }
