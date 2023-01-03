# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ProcurementGroup(models.Model):

    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        rental_location = self._context.get("force_rental_customer_location")
        if rental_location:
            self = self.with_context(force_rental_customer_location=False)
            location_id = rental_location
            for procurement in procurements:
                print ("6666666666666666666666", location_id)
                procurement.location_id = location_id.id
        return super(ProcurementGroup, self).run(procurements, raise_user_error=raise_user_error)
