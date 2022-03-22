# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestSaleOrderLine(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env["res.company"].create({"name": "Company"})

        cls.user = cls.env.ref("base.user_demo")
        cls.user.groups_id |= cls.env.ref("sales_team.group_sale_manager")
        cls.user.groups_id |= cls.env.ref("stock.group_stock_manager")
        cls.user.company_ids |= cls.company
        cls.user.company_id = cls.company

        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "W1", "code": "W1", "company_id": cls.company.id}
        )

        cls.location_1 = cls.warehouse.lot_stock_id
        cls.rental_location = cls.warehouse.lot_stock_id.copy(
            {"is_rental_stock_location": True}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "My Product", "type": "product"}
        )

    def _add_quant(self, product, location, qty):
        self.env["stock.quant"].create(
            {"location_id": location.id, "quantity": qty, "product_id": product.id}
        )

    def create_order_and_get_line(self, is_rental=False):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env.user.partner_id.id,
                "pricelist_id": self.env.ref("product.list0").id,
                "is_rental": is_rental,
                "warehouse_id": self.warehouse.id,
                "company_id": self.company.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

        return sale_order.order_line.sudo(self.user)

    def test_rental_sale_order(self):
        """
        Prerequisites :
        - Storable product
        - Two stock locations, one of which is a rental type

        Use case :
        - Setting quantities, 100 in rental stock location and 200 in the other
        - create a normal sale order

        Post-conditions :
        - Check if available_qty_for_popover is 200
        """
        self._add_quant(self.product, self.location_1, 200)
        self._add_quant(self.product, self.rental_location, 100)
        line = self.create_order_and_get_line(is_rental=True)
        assert line.available_qty_for_popover == 100

    def test_sale_order(self):
        """
        Prerequisites :
        - Storable product
        - Two stock locations, one of which is a rental type

        Use case :
        - Setting quantities, 100 in rental stock location and 200 in the other
        - create a normal sale order

        Post-conditions :
        - Check if available_qty_for_popover is 200
        """
        self._add_quant(self.product, self.location_1, 200)
        self._add_quant(self.product, self.rental_location, 100)
        line = self.create_order_and_get_line()
        assert line.available_qty_for_popover == 200
