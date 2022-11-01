# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models,api


class ResPartner(models.Model):

    _inherit = "res.partner"

    def get_available_delivery_carriers(self):
        privilege_level = self.get_privilege_level()
        privilege_level_carriers = privilege_level.mapped("delivery_carrier_ids")
        unfiltered_carriers = self.env["delivery.carrier"].search(
            [("privilege_level_ids", "=", False)]
        )
        return privilege_level_carriers | unfiltered_carriers

    @api.onchange("privilege_level_id")
    def onchange_privilege_level_id(self):
        if self.privilege_level_id.default_delivery_carrier_id:
            self.property_delivery_carrier_id = self.privilege_level_id.default_delivery_carrier_id.id
        else:
            self.property_delivery_carrier_id = False


