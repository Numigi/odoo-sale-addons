# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ChangeParentWizard(models.TransientModel):
    _name = "change.parent.warning.wizard"

    partner_id = fields.Many2one('res.partner')

    def action_confirm(self):
        self.ensure_one()
        vals = self._context.get('vals')
        self.partner_id.write(vals)
        return True
