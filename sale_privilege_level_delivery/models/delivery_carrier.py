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

        if "filter_delivery_carrier_ids" in self._context:
            available_ids = self._context["filter_delivery_carrier_ids"]
            res = res.filtered(lambda a: available_ids and a.id in available_ids)

        return res
