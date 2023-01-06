# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SalePrivilegeLevel(models.Model):
    _inherit = "sale.privilege.level"

    pricelist_ids = fields.One2many(
        "sale.privilege.level.pricelist", "privilege_level_id", "Pricelists"
    )
