# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SalePrivilegeLevel(models.Model):
    _inherit = "sale.privilege.level"

    default_delivery_carrier_id = fields.Many2oneb(
        "delivery.carrier",
        string="Default Delivery Method",
        help="This field allows you to select, among the Delivery Methods defined for this privilege level,"
             "the Delivery Method to be used by default for all partners belonging to this privilege level."
    )

    delivery_carrier_ids = fields.Many2many(
        "delivery.carrier",
        "sale_privilege_level_delivery_carrier_rel",
        "privilege_level_id",
        "carrier_id",
        "Delivery Carriers",
    )
