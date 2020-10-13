# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SalePrivilegeLevel(models.Model):

    _inherit = "sale.privilege.level"

    pricelist_ids = fields.Many2many(
        "product.pricelist",
        "sale_privilege_level_pricelist_rel",
        "privilege_level_id",
        "pricelist_id",
        "Pricelists",
    )
