# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.addons.sale.tests.test_sale_order import TestSaleOrder


@tagged('post_install', '-at_install')
class TestSOSelectSoLine(TestSaleOrder):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

    def test_select_batch_of_so_line(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.company_data['product_order_no'].id,
                    'product_uom_qty': -1,
                }),
                (0, 0, {
                    'product_id': self.company_data['product_order_no'].id,
                    'product_uom_qty': -1,
                }),

            ]
        })
        sale_order.select_lines = True
        sale_order._onchange_select_lines()
        self.assertTrue(
            all(line.select_line is True for line in sale_order.order_line))
        sale_order.order_line[0].select_line = False
        sale_order._compute_select_lines()
        self.assertFalse(sale_order.select_lines)
        sale_order.select_lines = True
        sale_order._onchange_select_lines()
        sale_order.select_lines = False
        sale_order._onchange_select_lines()
        self.assertTrue(
            not any(line.select_line for line in sale_order.order_line))
