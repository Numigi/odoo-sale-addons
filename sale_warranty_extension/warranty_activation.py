# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import models


class SaleWarranty(models.Model):

    _inherit = 'sale.warranty'

    def _get_active_extension_subscription(self):
        return self.env['sale.subscription'].search([
            ('in_progress', '=', True),
            ('partner_id.commercial_partner_id', '=',
                self.partner_id.commercial_partner_id.id),
            ('template_id', '=', self.type_id.extension_template_id.id),
        ], limit=1)

    def _should_be_extended(self):
        return (
            self.type_id.use_warranty_extension and
            bool(self._get_active_extension_subscription())
        )

    def _get_extension_start_date(self):
        return self.expiry_date + timedelta(1)

    def _get_extension_expiry_date(self):
        return self.expiry_date + relativedelta(months=self.type_id.extension_duration_in_months)

    def _activate_warranty(self, serial_number):
        """Extend the warranty on activation if it meets the requirements.

        In order to extend the warranty:
            1- The use_warranty_extension checkbox must be checked.
            2- The customer must have an active subscription.
            3- This subscription must have the subscription
               template defined on the warranty type.
        """
        super()._activate_warranty(serial_number)
        if self._should_be_extended():
            contract = self._get_active_extension_subscription()
            self.write({
                'use_warranty_extension': True,
                'extension_start_date': self._get_extension_start_date(),
                'extension_expiry_date': self._get_extension_expiry_date(),
                'extension_subscription_id': contract.id,
            })
