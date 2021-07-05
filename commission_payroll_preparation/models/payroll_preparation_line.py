# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class PayrollPreparationLine(models.Model):
    _inherit = "payroll.preparation.line"

    commission_target_id = fields.Many2one("commission.target", index=True)
    prorata = fields.Float()
    prorata_amount = fields.Float(readonly=True)

    @api.onchange("prorata")
    def onchange_prorata_amount(self):
        self.prorata_amount = self.prorata * self.amount
