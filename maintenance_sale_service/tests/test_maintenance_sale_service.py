from odoo.tests import common


class TestMaintenanceSaleService(common.SavepointCase):
    def setUp(self):
        super(TestMaintenanceSaleService, self).setUp()
        self.partner = self.env["res.partner"].create({"name": "Partner A"})
        self.model = self.env["maintenance.equipment.model"].create({"name": "Model A"})
        self.equipment = self.env["maintenance.equipment"].create(
            {
                "partner_id": self.partner.id,
                "model_id": self.model.id,
                "serial_no": "#1",
            }
        )

    def test_sale_product_with_equipment(self):
        product = self._create_service_product_task_new_project()
        sale = self._create_sale_order()
        sale_line = self._create_sale_order_line(sale, product, self.equipment)
        sale.action_confirm()
        self.assertEqual(sale_line.equipment_id, sale_line.task_id.equipment_id)
        self.assertEqual(sale_line.equipment_id, self.equipment)

    def test_sale_product_without_equipment(self):
        product = self._create_service_product_task_new_project()
        sale = self._create_sale_order()
        sale_line = self._create_sale_order_line(sale, product, False)
        sale.action_confirm()
        self.assertEqual(
            sale_line.task_id.equipment_id, self.env["maintenance.equipment"]
        )

    def _create_service_product_task_new_project(self):
        return self.env["product.product"].create(
            {
                "name": "Service Product",
                "type": "service",
                "service_tracking": "task_new_project",
            }
        )

    def _create_sale_order(self):
        return self.env["sale.order"].create({"partner_id": self.partner.id})

    def _create_sale_order_line(self, sale_order, product, equipment):
        return self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": product.id,
                "equipment_id": equipment and equipment.id or False,
                "product_uom_qty": 1,
                "name": "line",
            }
        )
