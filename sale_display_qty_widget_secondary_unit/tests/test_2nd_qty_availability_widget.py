# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo.addons.sale.tests.common import TestSaleCommon


class Test2ndQtyAvailabilityWidget(TestSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_virtual_2nd_unit_available_at_date(self):
        # sell two products
        item1 = self.company_data["product_order_no"]
        item1.type = "product"
        product_uom_kg = self.env.ref("uom.product_uom_kgm")
        product_uom_unit = self.env.ref("uom.product_uom_unit")
        item1.write(
            {
                "uom_id": product_uom_kg.id,
                "uom_po_id": product_uom_kg.id,
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "code": "A",
                            "name": "unit-700",
                            "uom_id": product_uom_unit.id,
                            "factor": 0.7,
                        },
                    )
                ],
            }
        )
        item1_product = item1.product_template_id.product_variant_ids[0]
        item1.product_tmpl_id.stock_secondary_uom_id = item1_product.secondary_uom_ids[
            0
        ].id

        warehouse1 = self.company_data["default_warehouse"]
        self.env["stock.quant"]._update_available_quantity(
            item1, warehouse1.lot_stock_id, 10
        )
        self.env["stock.quant"]._update_reserved_quantity(
            item1, warehouse1.lot_stock_id, 3
        )

        warehouse2 = self.env["stock.warehouse"].create(
            {
                "partner_id": self.partner_a.id,
                "name": "Numigi Warehouse",
                "code": "Numitest",
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            item1, warehouse2.lot_stock_id, 5
        )
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": item1.name,
                            "product_id": item1.id,
                            "product_uom_qty": 1,
                            "product_uom": item1.uom_id.id,
                            "price_unit": item1.list_price,
                        },
                    ),
                ],
            }
        )
        line = so.order_line[0]
        self.assertAlmostEqual(
            line.scheduled_date, datetime.now(), delta=timedelta(seconds=10)
        )
        self.assertEqual(line.virtual_available_at_date, 10)
        self.assertEqual(line.virtual_2nd_unit_available_at_date, 70)
        self.assertEqual(line.free_qty_today, 7)
        self.assertEqual(line.free_2nd_unit_qty_today, 49)
        so.warehouse_id = warehouse2
        # invalidate product cache to ensure qty_available is recomputed
        # bc warehouse isn't in the depends_context of qty_available
        line.product_id.invalidate_cache()
        self.assertEqual(line.virtual_available_at_date, 5)
        self.assertEqual(line.virtual_2nd_unit_available_at_date, 35)
        self.assertEqual(line.free_qty_today, 5)
        self.assertEqual(line.free_2nd_unit_qty_today, 35)
