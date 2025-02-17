# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError
from odoo import fields


class TestPartnerSaleTarget(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "company_type": "company"
            }
        )

        cls.target_1 = cls.env["sale.target"].create(
            {
                "partner_id": cls.partner.id,
                "date_start": "2023-01-01",
                "date_end": fields.Date.today(),
                "sale_target": 500,
            }
        )

        cls.sale_order_1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": "2023-06-01",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.env.ref("product.product_product_4").id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        cls.sale_order_1.action_confirm()
        cls.sale_order_1.write({"date_order": "2023-06-20"})

    def test_is_sale_target_allowed_contact(self):
        self.assertTrue(self.partner.is_sale_target_allowed_contact)

    def test_realized_target_calculation(self):
        self.assertEqual(self.target_1.realized_target, 100)

    def test_current_sale_target_and_realized(self):
        self.target_1.write({
            "date_start": "2023-01-02",
        })

        # Keep in mind that the current sale target is the sum of all sale targets
        # that are active today or have an end date greater than today
        # so even having old sale targets, the current sale must be the same
        self.assertEqual(self.partner.current_sale_target, 500)
        self.assertEqual(self.partner.current_realized_target, 0.2)  # 100/500

    def test_create_new_target(self):
        target_2 = self.env["sale.target"].create(
            {
                "partner_id": self.partner.id,
                "date_start": "2022-01-01",
                "date_end": "2022-05-20",
                "sale_target": 300,
            }
        )

        sale_order_2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "date_order": "2022-02-01",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "product_uom_qty": 1,
                            "price_unit": 200,
                        },
                    )
                ],
            }
        )
        sale_order_2.action_confirm()
        sale_order_2.write({"date_order": "2022-02-20"})

        self.assertEqual(target_2.realized_target, 200)
        self.assertEqual(self.partner.current_sale_target, 500)
        self.assertEqual(self.partner.current_realized_target, 0.2)

    def test_overlapping_target_validation(self):
        with self.assertRaises(ValidationError):
            self.env["sale.target"].create(
                {
                    "partner_id": self.partner.id,
                    "date_start": "2023-06-01",
                    "date_end": fields.Date.today(),
                    "sale_target": 500,
                }
            )
