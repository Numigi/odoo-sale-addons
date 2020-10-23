# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class Pricelist(models.Model):

    _inherit = "product.pricelist"

    privilege_level_ids = fields.Many2many(
        "sale.privilege.level",
        "sale_privilege_level_pricelist_rel",
        "pricelist_id",
        "privilege_level_id",
        "Privilege Levels",
    )

    def search(self, *args, **kwargs):
        res = super().search(*args, **kwargs)

        partner_id = self._context.get("sale_privilege_level_partner_id")
        if partner_id:
            partner = (
                self.env["res.partner"]
                .browse(partner_id)
                .with_context(sale_privilege_level_partner_id=False)
            )
            available_pricelists = partner.get_available_pricelists()
            res &= available_pricelists

        return res

    def _matches_company_id(self, company_id):
        return not self.company_id or self.company_id.id == company_id

    def _matches_country(self, country):
        if not self.country_group_ids:
            return True
        elif not country:
            return False
        else:
            return country in self.mapped("country_group_ids.country_ids")
