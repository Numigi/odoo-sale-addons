# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api


class ResPartner(models.Model):

    _inherit = "res.partner"

    def get_available_delivery_carriers(self):
        privilege_level = self.get_privilege_level()
        privilege_level_carriers = \
            privilege_level.mapped("delivery_carrier_ids")
        unfiltered_carriers = self.env["delivery.carrier"].search(
            [("privilege_level_ids", "=", False)]
        )
        return privilege_level_carriers | unfiltered_carriers

    @api.onchange("privilege_level_id")
    def onchange_privilege_level_id(self):
        if self.privilege_level_id.default_delivery_carrier_id:
            self.property_delivery_carrier_id = \
                self.privilege_level_id.default_delivery_carrier_id.id
        else:
            self.property_delivery_carrier_id = False

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for partner in self:
            if 'privilege_level_id' in vals:
                privilege_level_id = self.env['sale.privilege.level'].browse(
                    vals['privilege_level_id'])
                partner.property_delivery_carrier_id = \
                    privilege_level_id.default_delivery_carrier_id.id
        return res
