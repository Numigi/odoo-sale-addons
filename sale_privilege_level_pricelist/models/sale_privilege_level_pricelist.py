# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SalePrivilegeLevelPricelist(models.Model):

    _name = "sale.privilege.level.pricelist"
    _description = "Sale Privilege Level Pricelist"

    privilege_level_id = fields.Many2one(
        "sale.privilege.level", required=True, ondelete="cascade"
    )
    pricelist_id = fields.Many2one("product.pricelist", required=True)
    currency_id = fields.Many2one("product.pricelist", required=True)
