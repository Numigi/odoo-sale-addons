# © 2024 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.sale_project.tests.test_sale_project import TestSaleProject


class TestMilestone(TestSaleProject):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_sale_project_with_project_description(self):
        SaleOrderLine = self.env['sale.order.line'].with_context(
            tracking_disable=True)
        sale_order = self.env['sale.order'].with_context(tracking_disable=True).create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'project_description': "My Best Project For Test",
        })
        so_line_order_new_task_new_project = SaleOrderLine.create({
            'name': self.product_order_service3.name,
            'product_id': self.product_order_service3.id,
            'product_uom_qty': 10,
            'product_uom': self.product_order_service3.uom_id.id,
            'price_unit': self.product_order_service3.list_price,
            'order_id': sale_order.id,
        })
        so_line_order_only_project = SaleOrderLine.create({
            'name': self.product_order_service4.name,
            'product_id': self.product_order_service4.id,
            'product_uom_qty': 10,
            'product_uom': self.product_order_service4.uom_id.id,
            'price_unit': self.product_order_service4.list_price,
            'order_id': sale_order.id,
        })
        sale_order.action_confirm()
        #  service_tracking 'task_in_project'
        self.assertTrue(sale_order.project_description in (
            so_line_order_new_task_new_project.project_id.name),
            "Project name should contain the Sale Project Description")
        # service_tracking 'project_only'
        self.assertTrue(sale_order.project_description in (
            so_line_order_only_project.project_id.name),
            "Project name should contain the Sale Project Description")

        sale_order.write({"project_description": "My New Description"})
        self.assertTrue(sale_order.project_description in (
            so_line_order_new_task_new_project.project_id.name),
            "Project name should contain the Sale Updated Project Description")
