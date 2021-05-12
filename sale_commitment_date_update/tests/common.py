# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase
from datetime import datetime, timedelta


class SaleCommitmentDateCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.new_date = datetime(1990, 1, 25)
        cls.old_date = cls.new_date - timedelta(5)

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "william",
            }
        )

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "commitment_date": cls.old_date,
            }
        )

        cls.sale_order_line = cls.env["sale.order.line"].create(
            {
                "product_id": cls.product.id,
                "order_id": cls.sale_order.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1,
                "name": "line",
            }
        )

        cls.wizard = cls.env["sale.commitment.date.update"].create(
            {
                "order_id": cls.sale_order.id,
                "date": cls.new_date,
            }
        )

