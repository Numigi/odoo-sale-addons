# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SalePrivilegeLevelRentalPricelist(models.Model):

    _name = "sale.privilege.level.rental.pricelist"
    _inherit = "sale.privilege.level.pricelist"
    _description = "Sale Privilege Level Rental Pricelist"
    _order = "sequence"
