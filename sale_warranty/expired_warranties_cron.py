# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import models


class SaleWarranty(models.Model):
    """This class contains the logic related to ending warranties on expiration."""

    _inherit = 'sale.warranty'

    def expired_warranties_cron(self):
        """Update the state of warranties that are expired."""
        today = datetime.now().date()
        warranties_to_end = self.env['sale.warranty'].search([
            ('state', '=', 'active'),
            ('expiry_date', '<', today),
        ])
        warranties_to_end.write({'state': 'expired'})
