# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo import models


class SaleWarranty(models.Model):
    """This class contains the logic related to ending warranties on expiration."""

    _inherit = 'sale.warranty'

    def _find_warranties_to_set_expired(self):
        """Filter warranties to end based on the extension date.

        If the warranty has an extension and that the extension
        is not expired, then the warranty is kept active.
        """
        expired_warranties = super()._find_warranties_to_set_expired()
        today = datetime.now().date()
        return expired_warranties.filtered(
            lambda w: (
                not w.use_warranty_extension or
                not w.extension_expiry_date or
                w.extension_expiry_date < today
            )
        )
