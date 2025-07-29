# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockMove(models.Model):

    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        """On delivery, activate the waranties for the delivered products.

        Warranties are activated with sudo because stock users should not have
        access to modify warranties manually.
        """
        result = super()._action_done(cancel_backorder=cancel_backorder)

        for line in self.mapped('sale_line_id'):
            line.sudo().activate_warranties_for_delivered_products()

        return result
