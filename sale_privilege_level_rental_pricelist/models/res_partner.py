# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import threading
from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.depends("privilege_level_id", "country_id")
    def _compute_rental_pricelist(self):
        if _is_testing_other_module(self._context):
            return super()._compute_rental_pricelist()

        for partner in self:
            partner.rental_pricelist_id = partner.sudo()._get_rental_pricelist()

    def _get_rental_pricelist(self):
        privilege_level = self.get_privilege_level()
        pricelist_entries = (
            privilege_level.mapped("rental_pricelist_ids")
            .sorted("sequence")
            .filtered(lambda e: e.matches_partner(self))
        )
        return pricelist_entries.mapped("pricelist_id")[:1]


def _is_testing_other_module(context):
    return getattr(threading.currentThread(), "testing", False) and not context.get(
        "testing_sale_privilege_level_pricelist"
    )
