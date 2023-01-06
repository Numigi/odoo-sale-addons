# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    warranty_ids = fields.One2many(
        'sale.warranty',
        'sale_order_line_id',
        'Warranties',
    )

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """When procurements are triggered, generate warranties.

        This method is called either when the sale order is confirmed
        or when a new order line is added to a confirmed order.

        Warranties are generated with sudo because salesmen should not have
        access to modify warranties manually.
        """
        result = super()._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
        self.sudo().generate_missing_warranties()
        return result

    def generate_missing_warranties(self):
        """Generate all missing warranties for the given sale order lines."""
        for line in self:
            warranties_with_same_company = line.product_id.warranty_type_ids.filtered(
                lambda w: not w.company_id or w.company_id == line.company_id
            )
            for warranty_type in warranties_with_same_company:
                line._generate_missing_warranties_of_given_type(warranty_type)

    def _generate_missing_warranties_of_given_type(self, warranty_type):
        """Generate missing warranties of a specific type for a single order line.

        :param warranty_type: the type of warranty to generate.
        """
        required_warranty_count = max(int(self.product_uom_qty), 0)
        warranty_count = len(
            self.warranty_ids.filtered(
                lambda w: w.type_id == warranty_type and w.state != 'cancelled')
        )
        missing_warranty_count = required_warranty_count - warranty_count
        for _ in range(missing_warranty_count):
            self.env['sale.warranty'].create(self._prepare_warranty_values(warranty_type))

    def _prepare_warranty_values(self, warranty_type):
        """Prepare values for generating a warranty of a given type.

        :param warranty_type: the type of warranty to generate.
        :return: the sale.warranty values
        :rtype: dict
        """
        return {
            'type_id': warranty_type.id,
            'description': warranty_type.description,
            'sale_order_id': self.order_id.id,
            'sale_order_line_id': self.id,
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'partner_id': self.order_id.partner_id.commercial_partner_id.id,
            'state': 'pending',
        }

    def activate_warranties_for_delivered_products(self):
        if self.product_id.tracking == 'serial':
            self._activate_warranties_for_serialized_products()
        else:
            self._activate_warranties_for_unserialized_products()

    def _activate_warranties_for_serialized_products(self):
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
            warranty.action_activate(serial_number)

    def _activate_warranties_for_unserialized_products(self):
        pending_warranties = self.warranty_ids.filtered(lambda w: w.state == 'pending')

        activated_qty = len(self.warranty_ids.filtered(lambda w: w.activation_date))
        qty_to_activate = max(int(self.qty_delivered - activated_qty), 0)

        for warranty, dummy in zip(pending_warranties, range(qty_to_activate)):
            warranty.action_activate()
