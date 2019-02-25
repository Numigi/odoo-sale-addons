# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models


def activate_warranty(warranty, serial_number):
    """Activate a given warranty.

    :param warranty: the sale.warranty to activate
    :param serial_number: the stock.production.lot to link to the warranty
    """
    today = datetime.now().date()
    expiry_date = (
        today + relativedelta(months=warranty.type_id.duration_in_months) - timedelta(1)
    )
    warranty.write({
        'state': 'active',
        'lot_id': serial_number.id,
        'expiry_date': expiry_date,
        'activation_date': today,
    })


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    def _activate_warranty_for_delivered_products(self):
        """Activate the warranties for the delivered products.

        The matching between delivered serial numbers and pending warranties has 3 possible cases:

        1. Same number of warranties and serial numbers.

            Warranty 1 --> Serial 1
            Warranty 2 --> Serial 2

        2. More warranties than serial numbers.

            Warranty 1 --> Serial 1
            Warranty 2 --> Serial 2
            Warranty 3 --> Empty

        2. More serial numbers than pending warranties.

            This case is unexpected. This likely means that more products were shipped than ordered.
            In such rare case, a manual action from the sales manager is expected to fix the issue.

            Warranty 1 --> Serial 1
            Warranty 2 --> Serial 2
                           Serial 3 is not attached to a warranty.
        """
        pending_warranties = self.warranty_ids.filtered(lambda w: w.state == 'pending')

        activated_serial_numbers = self.mapped('warranty_ids.lot_id')
        delivery_lines = self.move_ids.filtered(lambda m: m.picking_type_id.code == 'outgoing')
        delivered_serial_numbers = delivery_lines.mapped('move_line_ids.lot_id')
        serial_numbers_to_activate = delivered_serial_numbers - activated_serial_numbers

        for warranty, serial_number in zip(pending_warranties, serial_numbers_to_activate):
            activate_warranty(warranty, serial_number)


class StockMove(models.Model):

    _inherit = 'stock.move'

    def _action_done(self):
        """On delivery, activate the waranties for the delivered products.

        Warranties are activated with sudo because stock users should not have
        access to modify warranties manually.
        """
        result = super()._action_done()

        delivery_moves = self.filtered(lambda m: m.picking_type_id.code == 'outgoing')
        sale_lines_to_update = delivery_moves.mapped('sale_line_id')
        for line in sale_lines_to_update:
            line.sudo()._activate_warranty_for_delivered_products()

        return result
