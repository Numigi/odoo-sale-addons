# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError
from odoo import fields


class TestPartnerSaleTarget(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_partner_sale_target(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "company_type": "company",
            }
        )
        partner._compute_is_sale_target_allowed_contact()

        self.assertTrue(partner.is_sale_target_allowed_contact)

        target_1 = self.env["sale.target"].create(
            {
                "partner_id": partner.id,
                "date_start": "2023-01-01",
                "date_end": fields.Date.today(),
                "sale_target": 500,
            }
        )

        # Check that the realized target is updated
        self.assertTrue(target_1.partner_id.is_sale_target_allowed_contact)

        # Create sale order that is linked to the sale target
        sale_order_1 = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "date_order": "2023-06-01",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        # Confirm the sale order
        sale_order_1.action_confirm()
        sale_order_1.write({"date_order": "2023-06-20"})

        # Check partner have sale_order_1_ids and its state is sale
        self.assertTrue(target_1.partner_id.sale_order_ids)
        self.assertEqual(target_1.partner_id.sale_order_ids[0].state, "sale")

        target_1._compute_realized_target()
        target_1._compute_realized()
        self.assertEqual(target_1.realized_target, 100)

        # Check the current sale target and current realized target
        partner._compute_current_sale_target()
        self.assertEqual(partner.current_sale_target, 500)
        self.assertEqual(partner.current_realized_target, 0.2)  # 100/500

        # Create a new sale target
        target_2 = self.env["sale.target"].create(
            {
                "partner_id": partner.id,
                "date_start": "2022-01-01",
                "date_end": "2022-05-20",
                "sale_target": 300,
            }
        )

        sale_order_2 = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
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
        # Confirm the sale order
        sale_order_2.action_confirm()
        sale_order_2.write({"date_order": "2022-02-20"})

        partner.sale_target_ids._compute_realized_target()
        partner.sale_target_ids._compute_realized()

        self.assertEqual(target_2.realized_target, 200)

        # Check again the current sale target and current realized target
        partner._compute_current_sale_target()
        # Keep in mind that the current sale target is the sum of all sale targets
        # that are active today or have an end date greater than today
        # so even having old sale targets, the current sale must be the same
        self.assertEqual(partner.current_sale_target, 500)
        self.assertEqual(partner.current_realized_target, 0.2)  # 100/800

        # Create sale target line with overlapping dates and check
        # if it raises a validation error
        with self.assertRaises(ValidationError):
            self.env["sale.target"].create(
                {
                    "partner_id": partner.id,
                    "date_start": "2023-06-01",
                    "date_end": fields.Date.today(),
                    "sale_target": 500,
                }
            )
