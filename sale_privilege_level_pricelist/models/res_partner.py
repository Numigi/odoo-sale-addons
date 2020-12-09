# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    property_product_pricelist = fields.Many2one(inverse=None)

    def _compute_product_pricelist(self):
        for partner in self:
            available_pricelists = partner.sudo()._get_available_pricelists()
            partner.property_product_pricelist = available_pricelists[:1]

    def _get_available_pricelists(self):
        privilege_level = (
            self.privilege_level_id or self.commercial_partner_id.privilege_level_id
        )
        pricelist_entries = privilege_level.pricelist_ids.sorted("sequence")
        pricelists = pricelist_entries.mapped("pricelist_id")
        return pricelists.filtered(lambda p: p._matches_country(self.country_id))
