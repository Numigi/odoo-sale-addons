# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    property_rental_pricelist = fields.Many2one(
        compute="_compute_property_rental_pricelist",
        company_dependent=False,
    )

    @api.depends("privilege_level_id", "country_id")
    def _compute_property_rental_pricelist(self):
        for partner in self:
            partner.property_rental_pricelist = partner.sudo()._get_rental_pricelist()

    def _get_rental_pricelist(self):
        privilege_level = self.get_privilege_level()
        pricelist_entries = (
            privilege_level.mapped("rental_pricelist_ids")
            .sorted("sequence")
            .filtered(lambda e: e.matches_partner(self))
        )
        return pricelist_entries.mapped("pricelist_id")[:1]
