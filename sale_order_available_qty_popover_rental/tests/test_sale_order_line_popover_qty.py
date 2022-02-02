# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase, tagged


@tagged('post_install', '-at_install', 'rental')
class TestSaleOrderLine(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderLine, cls).setUpClass()
        """Set data for testing sale_order_available_qty_popover_rental"""
        # create product
        cls.product = cls.env["product.product"].create(
            {"name": "My Article", "type": "product", "sale_ok": True, "list_price": 2400}
        )
        # get company
        cls.my_company = cls.env.ref("base.main_company")

        # create user
        Users = cls.env['res.users'].with_context(no_reset_password=True)
        cls.user = Users.create({
            'name': 'Andrew Manager',
            'login': 'manager',
            'email': 'a.m@example.com',
            'groups_id': [(6, 0, [cls.env.ref('sales_team.group_sale_manager').id])]
        })
        # warehouse
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "DP1", "code": "DP1", "company_id": cls.my_company.id}
        )

        # location
        cls.location_sales = cls.env['stock.location'].create(
            {
                "name": "Location Sales",
                "type": "internal",
                "parent_id": cls.warehouse.lot_stock_id.id,
                "is_rental_customer_location": False
            }
        )
        cls.location_rental = cls.env['stock.location'].create(
            {
                "name": "Location Rental",
                "type": "internal",
                "parent_id": cls.warehouse.lot_stock_id.id,
                "is_rental_customer_location": True
            }
        )

        # update inventory for each location
        cls.inventory_sale = cls.env['stock.inventory'].create({
            "name": "Iventory My Article Sales",
            "location_id": cls.location_sales.id,
            "filter": "product",
            "product_id": cls.product.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.product.id,
                        "location_id": cls.location_sales.id,
                        "product_qty": 15,
                    },
                )
            ],

        })
        cls.inventory_sale.action_start()
        cls.inventory_sale.action_validate()
        print("Sales Inventory ", cls.inventory_sale.line_ids)

        cls.inventory_rental = cls.env['stock.inventory'].create({
            "name": "Iventory My Article Rental",
            "location_id": cls.location_rental.id,
            "filter": "product",
            "product_id": cls.product.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.product.id,
                        "location_id": cls.location_rental.id,
                        "product_qty": 5,
                    },
                )
            ],
        })
        cls.inventory_rental.action_start()
        cls.inventory_rental.action_validate()
        print("Rental Inventory ", cls.inventory_rental.line_ids)

        # create sale order
        cls.sale_order_sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.user.partner_id.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.my_company.id,
                "is_rental": False,
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
        cls.line_sales = cls.sale_order_sale.order_line.sudo(cls.user)

        # create rental order
        cls.sale_order_rental = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.user.partner_id.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.my_company.id,
                "is_rental": True,
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
        cls.line_rental = cls.sale_order_rental.order_line.sudo(cls.user)

    def test_sale_order_line(self):
        """ Test sale order line qty popover """
        qty_sales = 15
        print("Sale Qty =", self.line_sales.available_qty_for_popover)
        assert self.line_sales.available_qty_for_popover == qty_sales

    def test_rental_order_line(self):
        """Test rental order line qty popover """
        qty_rental = 5
        print("Rental Qty =", self.line_rental.available_qty_for_popover)
        assert self.line_rental.available_qty_for_popover == qty_rental
