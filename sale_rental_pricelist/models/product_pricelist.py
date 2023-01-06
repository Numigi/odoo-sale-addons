# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Pricelist(models.Model):

    _inherit = "product.pricelist"

    rental = fields.Boolean()
