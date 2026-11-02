from odoo.tests.common import TransactionCase


class TestSaleStockAvailability(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 10.0,
                        },
                    )
                ],
            }
        )
        cls.line = cls.order.order_line[0]

    def test_fully_available_color(self):
        self._add_stock(20.0)
        assert self.line.qty_available_color == "text-success"

    def test_partially_available_color(self):
        self._add_stock(5.0)
        assert self.line.qty_available_color == "text-warning"

    def test_not_available_color(self):
        self._add_stock(0.0)
        assert self.line.qty_available_color == "text-danger"

    def test_reserved_qty_calculation(self):
        self.line.qty_available_today = 15.0
        self.line.free_qty_today = 10.0
        assert self.line.qty_reserved == 5.0

    def _add_stock(self, qty):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.env.ref("stock.stock_location_stock"), qty
        )
