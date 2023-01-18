# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create(
            {"name": "Customer A"}
        )
        cls.product_1 = cls.env["product.product"].create({"name": "Product 1"})
        cls.product_2 = cls.env["product.product"].create({"name": "Product 2"})
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "is_rental": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 100,
                            "price_unit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 100,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )
        cls.so.action_confirm()

    def test_not_yet_returned(self):
        assert self.so.return_rate == "0%"

    def test_partial_returned(self):
        rental_picking = self.so.picking_ids.filtered(
            lambda r: r.state not in ("done", "cancel")
            and any(r.move_lines.mapped("location_id.is_rental_customer_location"))
        )
        rental_picking.move_ids_without_package.write({"quantity_done": 10})
        rental_picking.button_validate()
        rental_picking.move_ids_without_package._action_done()
        assert self.so.return_rate == "10%"

    def test_fully_returned(self):
        rental_picking = self.so.picking_ids.filtered(
            lambda r: r.state not in ("done", "cancel")
            and any(r.move_lines.mapped("location_id.is_rental_customer_location"))
        )
        rental_picking.move_ids_without_package.write({"quantity_done": 100})
        rental_picking.button_validate()
        assert self.so.return_rate == "100%"

    def test_if_no_stockable_product_then_fully_returned(self):
        product_3 = self.env["product.product"].create(
            {"name": "Product 3", "type": "service"}
        )
        so = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "is_rental": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_3.id,
                            "product_uom_qty": 100,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        so.action_confirm()
        assert so.return_rate == "100%"
