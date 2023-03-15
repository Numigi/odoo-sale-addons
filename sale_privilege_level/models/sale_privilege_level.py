# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SalePrivilegeLevel(models.Model):
    _name = "sale.privilege.level"
    _description = "Sale Privilege Level"
    _order = "sequence"

    sequence = fields.Integer()
    name = fields.Char(required=True, translate=True)
    description = fields.Char(translate=True)
    active = fields.Boolean(default=True)

    partner_ids = fields.One2many("res.partner", "privilege_level_id")
