# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def _cart_update(self, *args, **kwargs):
        res = super()._cart_update(*args, **kwargs)

        for line in self.order_line:
            line._update_displayed_delay()

        return res
