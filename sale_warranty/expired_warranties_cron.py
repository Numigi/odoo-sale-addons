# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import models


class SaleWarranty(models.Model):
    """This class contains the logic related to ending warranties on expiration."""

    _inherit = 'sale.warranty'

    def _find_warranties_to_set_expired(self):
        """Find active warranties that must be set to expired.

        :rtype: sale.warranty recordset
        """
        return self.env['sale.warranty'].search([
            ('state', '=', 'active'),
            ('expiry_date', '<', datetime.now().date()),
        ])

    def expired_warranties_cron(self):
        """Update the state of warranties that are expired."""
        warranties_to_end = self._find_warranties_to_set_expired()
        warranties_to_end.write({'state': 'expired'})
