# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase
from ..models.sale_order_line import RED, YELLOW, GREEN


class TestSaleOrderLine(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {"name": "My Product", "type": "product"}
        )

        cls.company_1 = cls.env["res.company"].create({"name": "C1"})
        cls.company_2 = cls.env["res.company"].create({"name": "C2"})

        cls.user = cls.env.ref("base.user_demo")
        cls.user.groups_id |= cls.env.ref("sales_team.group_sale_manager")
        cls.user.company_ids |= cls.company_1
        cls.user.company_id = cls.company_1

        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {"name": "W1", "code": "W1", "company_id": cls.company_1.id}
        )

        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {"name": "W2", "code": "W2", "company_id": cls.company_1.id}
        )

        cls.location_1 = cls.warehouse_1.lot_stock_id
        cls.location_1.is_rental_stock_location = True
        cls.location_2 = cls.warehouse_2.lot_stock_id
        cls.location_2.is_rental_stock_location = False

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.user.partner_id.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "warehouse_id": cls.warehouse_1.id,
                "company_id": cls.company_1.id,
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
        cls.sale_order1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.user.partner_id.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "warehouse_id": cls.warehouse_1.id,
                "company_id": cls.company_1.id,
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

        cls.line = cls.sale_order.order_line.sudo(cls.user)
        cls.line1 = cls.sale_order1.order_line.sudo(cls.user)

        cls.almost_out_of_stock_qty = 5
        cls.env["ir.config_parameter"].set_param(
            "sale_order_available_qty_popover.almost_out_of_stock_qty",
            cls.almost_out_of_stock_qty,
        )

    def test_one_quant_true_is_rental_stock_location(self):
        qty = 10
        self._add_quant(self.product, self.location_1, qty)
        assert self.line.available_qty_for_popover == qty

    def test_one_quant_false_is_rental_stock_location(self):
        qty = 10
        self._add_quant(self.product, self.location_2, qty)
        assert self.line1.available_qty_for_popover == qty

    def test_two_quants_in_different_warehoues(self):
        qty_1 = 10
        qty_2 = 20
        self._add_quant(self.product, self.location_1, qty_1)
        self._add_quant(self.product, self.location_2, qty_2)
        assert self.line.available_qty_for_popover == qty_1
        assert self.line1.available_qty_for_popover == qty_2

    def _add_quant(self, product, location, qty):
        self.env["stock.quant"].create(
            {"location_id": location.id, "quantity": qty, "product_id": product.id}
        )
