# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SalePrivilegeLevel(models.Model):
    _inherit = "sale.privilege.level"

    default_delivery_carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Default Delivery Method",
        help="This field allows you to select, among the Delivery Methods"
             "defined for this privilege level, the Delivery Method to be used"
             "by default for all partners belonging to this privilege level."
    )

    delivery_carrier_ids = fields.Many2many(
        "delivery.carrier",
        "sale_privilege_level_delivery_carrier_rel",
        "privilege_level_id",
        "carrier_id",
        "Delivery Carriers",
    )

    def write(self, vals):
        res = super(SalePrivilegeLevel, self).write(vals)
        for level in self:
            if 'default_delivery_carrier_id' in vals:
                if level.partner_ids:
                    for partner in level.partner_ids:
                        partner.property_delivery_carrier_id = \
                            vals['default_delivery_carrier_id']
        return res
