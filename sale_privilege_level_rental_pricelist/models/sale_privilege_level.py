# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SalePrivilegeLevel(models.Model):

    _inherit = "sale.privilege.level"

    rental_pricelist_ids = fields.One2many(
        "sale.privilege.level.rental.pricelist",
        "privilege_level_id",
        "Rental Pricelists",
    )
