# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        procurements_list = []
        rental_location = self._context.get("force_rental_customer_location")
        for procurement in procurements:
            if rental_location:
                self = self.with_context(force_rental_customer_location=False)
                procurements_list.append(
                    self.env["procurement.group"].Procurement(
                        procurement.product_id,
                        procurement.product_qty,
                        procurement.product_uom,
                        rental_location,
                        procurement.name,
                        procurement.origin,
                        procurement.company_id,
                        procurement.values,
                    )
                )
            else:
                procurements_list.append(procurement)
        return super(ProcurementGroup, self).run(
            procurements_list, raise_user_error=raise_user_error
        )
