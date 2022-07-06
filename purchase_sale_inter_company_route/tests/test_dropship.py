# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class SaleOrderCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "My Customer"})
        cls.supplier = cls.env["res.partner"].create({"name": "My Supplier"})

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        cls.product = cls.env["product.product"].create(
            {
                "name": "My Product",
                "type": "product",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.supplier.id,
                        },
                    )
                ],
            }
        )

        cls.order = cls._create_sale_order()
        cls.order_line = cls.order.order_line

    @classmethod
    def _create_sale_order(cls):
        order_line_vals = cls._make_sale_order_line_vals()
        return cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "order_line": [(0, 0, order_line_vals)],
            }
        )

    @classmethod
    def _make_sale_order_line_vals(cls):
        return {
            "name": cls.product.display_name,
            "product_id": cls.product.id,
            "product_uom": cls.product.uom_id.id,
            "product_qty": 1,
            "price_unit": 100,
        }

    @classmethod
    def process_picking(cls, picking):
        for line in picking.move_line_ids:
            line.qty_done = 1

        picking.action_assign()
        picking.action_done()

    @classmethod
    def create_return_picking(cls, picking, to_refund=False):
        wizard_obj = cls.env["stock.return.picking"].with_context(active_id=picking.id)
        values = wizard_obj.default_get(list(wizard_obj._fields))
        wizard = wizard_obj.create(values)
        wizard.product_return_moves.quantity = 1
        wizard.product_return_moves.to_refund = to_refund
        return_picking_id = wizard.create_returns()["res_id"]
        return cls.env["stock.picking"].browse(return_picking_id)


class TestDropship(SaleOrderCase):
    """Test a case of a sale order with the dropship route.

    This checks that the module does not break standard behavior of dropshipping.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order_line.route_id = cls.env.ref("stock_dropshipping.route_drop_shipping")
        cls.order.action_confirm()

        cls.purchase_order = cls.env["purchase.order"].search(
            [("order_line.product_id", "=", cls.product.id)],
            limit=1,
        )
        cls.purchase_order.button_confirm()

    def test_dropshipping_return(self):
        picking = self.purchase_order.picking_ids
        self.process_picking(picking)

        assert self.order_line.qty_delivered == 1

        return_picking = self.create_return_picking(picking, to_refund=True)
        self.process_picking(return_picking)

        assert self.order_line.qty_delivered == 0

    def test_dropshipping_return__no_refund(self):
        picking = self.purchase_order.picking_ids
        self.process_picking(picking)

        assert self.order_line.qty_delivered == 1

        return_picking = self.create_return_picking(picking, to_refund=False)
        self.process_picking(return_picking)

        assert self.order_line.qty_delivered == 1
