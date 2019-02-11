# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    """This class contains the logic related to generating warranties from sales."""

    _inherit = 'sale.order.line'

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

    def _generate_missing_warranties(self):
        """Generate all missing warranties for the given sale order lines."""
        lines_with_serialized_product = self.filtered(lambda l: l.product_id.tracking == 'serial')
        for line in lines_with_serialized_product:
            for warranty_type in line.product_id.warranty_type_ids:
                line._generate_missing_warranties_of_given_type(warranty_type)

    @api.multi
    def _action_launch_stock_rule(self):
        """When procurements are triggered, generate warranties.

        This method is called either when the sale order is confirmed
        or when a new order line is added to a confirmed order.

        Warranties are generated with sudo because salesmen should not have
        access to modify warranties manually.
        """
        result = super()._action_launch_stock_rule()
        self.sudo()._generate_missing_warranties()
        return result
