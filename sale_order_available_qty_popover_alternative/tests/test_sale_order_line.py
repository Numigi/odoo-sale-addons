# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import tagged
from odoo.addons.sale_order_available_qty_popover.tests.test_sale_order_line import TestSaleOrderLine

YELLOW = "#fad817"
RED = "#ee1010"


@tagged('post_install')
class TestSaleOrderLine(TestSaleOrderLine):

    def create_order_and_get_line(self, qty, warehouse_id):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env.user.partner_id.id,
                "pricelist_id": self.env.ref("product.list0").id,
                "warehouse_id": warehouse_id.id,
                "company_id": self.company_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": qty,
                        },
                    )
                ],
            }
        )

        return sale_order.order_line.sudo(self.user)

    def _add_quant(self, product, location, qty):
        self.env["stock.quant"].create(
            {"location_id": location.id, "quantity": qty, "product_id": product.id}
        )

    def test_color_yellow(self):
        """
        Prerequisites :
        - Storable product
        - 2 warehouses locations

        Use case :
        - Setting quantities, 16 in warehouse1 , 20 in warehouse2
        - create a normal sale order
        - set warehouse_id equal to warehouse1
        - set product qty equal to 17

        Post-conditions :
        - Check if available_qty_for_popover is 16
        - Check if available_qty_popover_color is yellow
        """
        self._add_quant(self.product, self.location_1, 16)
        self._add_quant(self.product, self.location_2, 20)
        line = self.create_order_and_get_line(17, self.warehouse_1)
        assert line.available_qty_popover_color == YELLOW

    def test_color_red(self):
        """
        Prerequisites :
        - Storable product
        - 2 warehouses locations

        Use case :
        - Setting quantities, 16 in warehouse1 , 20 in warehouse2
        - create a normal sale order
        - set warehouse_id equal to warehouse2
        - set product qty equal to 37

        Post-conditions :
        - Check if available_qty_for_popover is 16
        - Check if available_qty_popover_color is yellow
        """
        self._add_quant(self.product, self.location_1, 16)
        self._add_quant(self.product, self.location_2, 20)
        line = self.create_order_and_get_line(37, self.warehouse_2)
        assert line.available_qty_for_popover == 20
        assert line.available_qty_popover_color == RED

    def test_two_quants_in_different_warehoues(self):
        self._add_quant(self.product, self.location_1, 16)
        self._add_quant(self.product, self.location_2, 20)
        line = self.create_order_and_get_line(17, self.warehouse_1)
        assert line.available_qty_for_popover == 16
