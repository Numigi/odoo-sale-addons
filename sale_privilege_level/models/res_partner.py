# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _default_privilege_level(self):
        return self.env.user.company_id.default_privilege_level_id

    privilege_level_id = fields.Many2one(
        "sale.privilege.level", ondelete="restrict", default=_default_privilege_level
    )

    privilege_level_invisible = fields.Boolean(
        compute="_compute_privilege_level_invisible"
    )

    @api.onchange("parent_id")
    def _onchange_parent_to_privilege_level(self):
        for partner in self:
            if partner.parent_id:
                partner.privilege_level_id = (
                    partner.parent_id.privilege_level_id.id or False
                )

    @api.depends("parent_id")
    def _compute_privilege_level_invisible(self):
        for partner in self:
            partner.privilege_level_invisible = partner != partner.commercial_partner_id

    def get_privilege_level(self):
        return self.commercial_partner_id.privilege_level_id

    def get_privilege_level_from_parent(self, parent_id=False):
        if parent_id:
            return self.search([("id", "=", parent_id)]).privilege_level_id.id or False

    def write(self, vals):
        if "parent_id" in vals:
            vals.update(
                {
                    "privilege_level_id": self.get_privilege_level_from_parent(
                        vals["parent_id"]
                    ),
                }
            )
        return super().write(vals)
