from odoo.tests.common import TransactionCase


class TestSaleStockAvailability(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls._create_storable_product(cls.env)
        cls.order = cls._create_sale_order(cls.env, cls.product)
        cls.line = cls.order.order_line[0]

    def test_fully_available_color(self):
        self._update_stock_quantity(20.0)
        assert self.line.qty_available_color == "text-success"

    def test_partially_available_color(self):
        self._update_stock_quantity(5.0)
        assert self.line.qty_available_color == "text-warning"

    def test_not_available_color(self):
        assert self.line.qty_available_color == "text-danger"

    def test_reserved_qty_calculation(self):
        self._update_stock_quantity(15.0)
        self._reserve_stock_quantity(5.0)
        assert self.line.qty_reserved == 5.0

    def test_force_widget_display(self):
        self.order.action_confirm()
        self.line.invalidate_recordset()
        assert self.line.display_qty_widget is True

    @classmethod
    def _create_storable_product(cls, env):
        return env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
            }
        )

    @classmethod
    def _create_sale_order(cls, env, product):
        return env["sale.order"].create(
            {
                "partner_id": env.ref("base.res_partner_1").id,
                "order_line": [
                    (0, 0, {"product_id": product.id, "product_uom_qty": 10.0})
                ],
            }
        )

    def _update_stock_quantity(self, quantity):
        location = self.env.ref("stock.stock_location_stock")
        self.env["stock.quant"]._update_available_quantity(
            self.product, location, quantity
        )
        self.line.invalidate_recordset()

    def _reserve_stock_quantity(self, reserved_quantity):
        location = self.env.ref("stock.stock_location_stock")
        self.env["stock.quant"]._update_available_quantity(
            self.product, location, reserved_quantity=reserved_quantity
        )
        self.line.invalidate_recordset()
