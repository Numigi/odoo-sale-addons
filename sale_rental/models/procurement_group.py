# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ProcurementRule(models.Model):

    _inherit = "procurement.group"

    @api.model
    def run(
        self, product_id, product_qty, product_uom, location_id, name, origin, values
    ):
        rental_location = self._context.get("force_rental_customer_location")
        if rental_location:
            self = self.with_context(force_rental_customer_location=False)
            location_id = rental_location

        return super(ProcurementRule, self).run(
            product_id, product_qty, product_uom, location_id, name, origin, values
        )
