# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import threading
from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    property_product_pricelist = fields.Many2one(inverse=None)

    def _compute_product_pricelist(self):
        if _is_testing_other_module(self._context):
            return super()._compute_product_pricelist()

        for partner in self:
            available_pricelists = partner.sudo()._get_available_pricelists()
            partner.property_product_pricelist = available_pricelists[:1]

    def _get_available_pricelists(self):
        privilege_level = self.get_privilege_level()
        pricelist_entries = privilege_level.mapped("pricelist_ids").sorted("sequence")
        pricelists = pricelist_entries.mapped("pricelist_id")
        return pricelists.filtered(lambda p: p._matches_country(self.country_id))


def _is_testing_other_module(context):
    return getattr(threading.currentThread(), "testing", False) and not context.get(
        "testing_sale_privilege_level_pricelist"
    )
