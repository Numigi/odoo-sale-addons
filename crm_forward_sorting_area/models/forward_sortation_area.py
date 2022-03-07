# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ForwardSortationAera(models.Model):

    _inherit = "forward.sortation.area"

    lead_ids = fields.One2many("crm.lead", "fsa_id", string="Leads")

    @api.multi
    def write(self, vals):
        res = super(ForwardSortationAera, self).write(vals)
        if "name" in vals:
            self.mapped("lead_ids")._compute_fsa_id()
            self.env["crm.lead"].search(
                [
                    ("zip", "ilike", vals["name"] + "%"),
                ]
            )._compute_fsa_id()

        return res
