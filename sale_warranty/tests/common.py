# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class SaleWarrantyCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.salesman = cls.env["res.users"].create(
            {
                "name": "Salesman",
                "login": "test_salesman",
                "email": "test_salesman@test.com",
                "groups_id": [(4, cls.env.ref("sales_team.group_sale_salesman").id)],
            }
        )

        cls.stock_user = cls.env["res.users"].create(
            {
                "name": "Stock User",
                "login": "test_stock_user",
                "email": "test_stock_user@test.com",
                "groups_id": [(4, cls.env.ref("stock.group_stock_user").id)],
            }
        )

        cls.warranty_6_months = cls.env["sale.warranty.type"].create(
            {
                "name": "6 Months Parts",
                "duration_in_months": 6,
                "description": "Warranted 6 months on parts",
            }
        )

        cls.warranty_2_years = cls.env["sale.warranty.type"].create(
            {
                "name": "2 Years Parts",
                "duration_in_months": 24,
                "description": "Warranted 2 years on parts",
            }
        )

        cls.product_a = cls.env["product.product"].create(
            {
                "name": "My Product",
                "tracking": "serial",
                "type": "product",
                "warranty_type_ids": [(4, cls.warranty_6_months.id)],
            }
        )

        cls.product_b = cls.env["product.product"].create(
            {
                "name": "My Product B",
                "tracking": "serial",
                "type": "product",
                "warranty_type_ids": [(4, cls.warranty_2_years.id)],
            }
        )

        cls.customer_company = cls.env["res.partner"].create(
            {"name": "Customer Company", "is_company": True}
        )

        cls.customer = cls.env["res.partner"].create(
            {
                "name": "My Customer",
                "parent_id": cls.customer_company.id,
            }
        )

        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.user.company_id.id)]
        )

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "user_id": cls.salesman.id,
                "warehouse_id": cls.warehouse.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_a.id,
                            "name": cls.product_a.name,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

    @classmethod
    def confirm_sale_order(cls):
        cls.sale_order.sudo(cls.salesman).action_confirm()

    @classmethod
    def generate_serial_number(cls, product, number):
        serial = cls.env["stock.production.lot"].create({
            "name": number,
            "product_id": product.id,
            'company_id': cls.env.company.id
        })
        cls.add_product_to_stock(product, 1, serial)
        return serial

    @classmethod
    def add_product_to_stock(cls, product, qty, serial=None):
        inventory = cls.env["stock.inventory"].create({"name": "Add product"})
        inventory.action_start()
        inventory.write(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_qty": qty,
                            "prod_lot_id": serial.id if serial else None,
                            "location_id": cls.warehouse.lot_stock_id.id,
                        },
                    )
                ]
            }
        )
        inventory.action_validate()


class WarrantyActivationCase(SaleWarrantyCase):
    def validate_picking(cls, picking):
        picking.sudo(cls.stock_user)._action_done()

    @classmethod
    def select_serial_numbers_on_picking(cls, picking, serial_numbers):
        for serial in serial_numbers:
            cls.select_product_on_picking(picking, serial.product_id, 1, serial)

    @classmethod
    def select_product_on_picking(cls, picking, product, qty, serial_number=None):
        move = picking.move_lines.filtered(lambda m: m.product_id == product)[:1]
        move_line_vals = {
            "location_dest_id": move.location_dest_id.id,
            "location_id": move.location_id.id,
            "lot_id": serial_number.id if serial_number else None,
            "product_id": product.id,
            "product_uom_id": move.product_uom.id,
            "qty_done": 1,
        }
        line_without_qty = move.move_line_ids.filtered(lambda l: not l.qty_done)[:1]
        if line_without_qty:
            line_without_qty.write(move_line_vals)
        else:
            move.write({"move_line_ids": [(0, 0, move_line_vals)]})
