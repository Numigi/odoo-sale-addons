# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def update_prices(self):
        super().update_prices()
        return True
