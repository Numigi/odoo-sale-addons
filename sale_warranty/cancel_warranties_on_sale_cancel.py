# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def action_cancel(self):
        """Cancel the warranties when the sale order is cancelled."""
        result = super().action_cancel()
        self.warranty_ids.sudo().write({'state': 'cancelled'})
        return result
