# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    property_product_pricelist = fields.Many2one(inverse=None)

    def _compute_product_pricelist(self):
        for partner in self:
            available_pricelists = partner._get_available_pricelists()
            partner.property_product_pricelist = available_pricelists[:1]

    def _get_available_pricelists(self):
        privilege_level = (
            self.privilege_level_id or self.commercial_partner_id.privilege_level_id
        )
        pricelists = privilege_level.mapped("pricelist_ids.pricelist_id").sorted(
            "sequence"
        )
        return pricelists.filtered(lambda p: p._matches_country(self.country_id))
