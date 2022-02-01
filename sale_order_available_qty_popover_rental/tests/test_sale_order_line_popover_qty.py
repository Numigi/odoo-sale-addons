# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase, tagged

@tagged('rental')
class TestSaleOrderLine(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderLine, cls).setUpClass()

    def test_sale_order_line(self):
        """ Test sale order line qty popover """
        # to do : finish test
        sale_order_line = self.env['sale.order.line'].create({
            'name': self.product_no_expense.name,
            'product_id': self.product_no_expense.id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'product_uom': self.product_no_expense.uom_id.id,
            'price_unit': self.product_no_expense.list_price,
            'order_id': self.sale_order.id,
        })
