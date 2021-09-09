# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class DeliveryCarrier(models.Model):

    _inherit = "delivery.carrier"

    privilege_level_ids = fields.Many2many(
        "sale.privilege.level",
        "sale_privilege_level_delivery_carrier_rel",
        "carrier_id",
        "privilege_level_id",
        "Privilege Levels",
    )

    def search(self, *args, **kwargs):
        res = super().search(*args, **kwargs)

        partner_id = self._context.get("sale_privilege_level_partner_id")
        if partner_id:
            partner = (
                self.env["res.partner"]
                .browse(partner_id)
                .with_context(sale_privilege_level_partner_id=False)
            )
            available_carriers = partner.get_available_delivery_carriers()
            res &= available_carriers

        return res
