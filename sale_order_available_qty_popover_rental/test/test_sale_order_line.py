from odoo.tests.common import SavepointCase


class TestSaleOrderLine(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {"name": "My Product", "type": "product"}
        )

        cls.company_1 = cls.env["res.company"].create({"name": "C1"})

        cls.user = cls.env.ref("base.user_demo")
        cls.user.groups_id |= cls.env.ref("sales_team.group_sale_manager")
        cls.user.company_ids |= cls.company_1
        cls.user.company_id = cls.company_1

        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {"name": "W1", "code": "W1", "company_id": cls.company_1.id}
        )

        cls.location_1 = cls.warehouse_1.lot_stock_id
        cls.location_2 = cls.warehouse_1.lot_stock_id

        cls.location_2.is_rental_stock_location = True

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.user.partner_id.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "warehouse_id": cls.warehouse_1.id,
                "company_id": cls.company_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

        cls.line = cls.sale_order.order_line.sudo(cls.user)

    def test_stock_quant(self):
        qty = 10
        self._add_quant(self.product, self.location_1, qty)
        assert self.line.available_qty_for_popover == qty

    def test_rent_quant(self):
        qty = 10
        self._add_quant(self.product, self.location_2, qty)
        assert self.line.available_qty_for_popover == 0

    def test_the_two_quants(self):
        qty_1 = 10
        qty_2 = 20
        self._add_quant(self.product, self.location_1, qty_1)
        self._add_quant(self.product, self.location_2, qty_2)
        assert self.line.available_qty_for_popover == qty_1

    def _add_quant(self, product, location, qty):
        self.env["stock.quant"].create(
            {"location_id": location.id, "quantity": qty, "product_id": product.id}
        )
