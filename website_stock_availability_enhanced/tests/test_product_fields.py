# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestProductFields(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "My Product",
                "type": "product",
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.receipt_type = cls.warehouse.in_type_id

    def test_sale_availability(self):
        self.product.compute_availability()
        assert self.product.sale_availability == 0

    def test_sale_availability__quants(self):
        self._add_stock_quant(1, self.stock_location)
        self.product.compute_availability()
        assert self.product.sale_availability == 1

    def test_sale_availability__quants_in_wrong_location(self):
        self._add_stock_quant(1, self.customer_location)
        self.product.compute_availability()
        assert self.product.sale_availability == 0

    def test_sale_availability__delivery(self):
        self._add_stock_move(1, self.stock_location, self.customer_location)
        self.product.compute_availability()
        assert self.product.sale_availability == -1

    def test_sale_availability__delivery_done(self):
        move = self._add_stock_move(1, self.stock_location, self.customer_location)
        move.state = "done"
        self.product.compute_availability()
        assert self.product.sale_availability == 0

    def test_sale_availability__dropship(self):
        move = self._add_stock_move(1, self.supplier_location, self.customer_location)
        self.product.compute_availability()
        assert self.product.sale_availability == 0

    def test_replenishment_availability(self):
        self.product.compute_availability()
        assert self.product.replenishment_availability == 0

    def test_replenishment_availability__include_sale_availability(self):
        self._add_stock_quant(1, self.stock_location)
        self.product.compute_availability()
        assert self.product.replenishment_availability == 1

    def test_replenishment_availability__receipt(self):
        self._add_stock_move(
            1, self.supplier_location, self.stock_location, picking_type=self.receipt_type
        )
        self.product.compute_availability()
        assert self.product.replenishment_availability == 1

    def test_replenishment_availability__receipt_with_two_moves(self):
        self._add_stock_move(
            1, self.supplier_location, self.stock_location, picking_type=self.receipt_type
        )
        self._add_stock_move(
            1, self.supplier_location, self.stock_location, picking_type=self.receipt_type
        )
        self.product.compute_availability()
        assert self.product.replenishment_availability == 2

    def _add_stock_quant(self, quantity, location):
        return self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": location.id,
                "quantity": quantity,
            }
        )

    def _add_stock_move(self, quantity, src_location, dest_location, picking_type=None):
        move = self.env["stock.move"].create(
            {
                "name": "/",
                "product_id": self.product.id,
                "product_uom_qty": quantity,
                "location_id": src_location.id,
                "location_dest_id": dest_location.id,
                "product_uom": self.product.uom_id.id,
                "picking_type_id": picking_type.id if picking_type else None,
            }
        )
        move._action_confirm()
        return move
