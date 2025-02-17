# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from collections import OrderedDict
from odoo.tools import float_compare


class TestSaleDoubleValidation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        context_no_mail = {
            "no_reset_password": True,
            "mail_create_nosubscribe": True,
            "mail_create_nolog": True,
        }
        group_salemanager = cls.env.ref("sales_team.group_sale_manager")
        group_salesman = cls.env.ref("sales_team.group_sale_salesman")
        group_employee = cls.env.ref("base.group_user")
        cls.user_manager = cls.env["res.users"].create(
            {
                "name": "User Officer",
                "login": "user_manager",
                "email": "usermanager@test.com",
                "groups_id": [(6, 0, [group_salemanager.id, group_employee.id])],
            }
        )
        cls.user_employee = cls.env["res.users"].create(
            {
                "name": "User Empployee",
                "login": "user_emp",
                "email": "useremp@test.com",
                "groups_id": [(6, 0, [group_salesman.id, group_employee.id])],
            }
        )
        Partner = cls.env["res.partner"].with_context(context_no_mail)
        cls.partner_customer_usd = Partner.create(
            {
                "name": "Customer from the North",
                "email": "customer.usd@north.com",
                "customer_rank": 1,
            }
        )
        # Products
        uom_unit = cls.env.ref("uom.product_uom_unit")
        uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.product_order = cls.env["product.product"].create(
            {
                "name": "Zed+ Antivirus",
                "standard_price": 235.0,
                "list_price": 280.0,
                "type": "consu",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "invoice_policy": "order",
                "expense_policy": "no",
                "default_code": "PROD_ORDER",
                "service_type": "manual",
                "taxes_id": False,
            }
        )
        cls.service_deliver = cls.env["product.product"].create(
            {
                "name": "Cost-plus Contract",
                "standard_price": 200.0,
                "list_price": 180.0,
                "type": "service",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "invoice_policy": "delivery",
                "expense_policy": "no",
                "default_code": "SERV_DEL",
                "service_type": "manual",
                "taxes_id": False,
            }
        )
        cls.service_order = cls.env["product.product"].create(
            {
                "name": "Prepaid Consulting",
                "standard_price": 40.0,
                "list_price": 90.0,
                "type": "service",
                "uom_id": uom_hour.id,
                "uom_po_id": uom_hour.id,
                "invoice_policy": "order",
                "expense_policy": "no",
                "default_code": "PRE-PAID",
                "service_type": "manual",
                "taxes_id": False,
            }
        )
        cls.product_deliver = cls.env["product.product"].create(
            {
                "name": "Switch, 24 ports",
                "standard_price": 55.0,
                "list_price": 70.0,
                "type": "consu",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "invoice_policy": "delivery",
                "expense_policy": "no",
                "default_code": "PROD_DEL",
                "service_type": "manual",
                "taxes_id": False,
            }
        )

        cls.product_map = OrderedDict(
            [
                ("prod_order", cls.product_order),
                ("serv_del", cls.service_deliver),
                ("serv_order", cls.service_order),
                ("prod_del", cls.product_deliver),
            ]
        )

    def test_one_step(self):
        self.user_employee.company_id.sudo().so_double_validation = "one_step"
        so = self.create_so_by_user_employee()
        # confirm quotation
        self.assertEqual(so.state, "draft")

    def test_two_steps_under_limit(self):
        self.user_employee.company_id.sudo().so_double_validation = "two_step"
        self.user_employee.company_id.sudo().so_double_validation_amount = 100000
        so = self.create_so_by_user_employee()
        # confirm quotation
        self.assertEqual(so.state, "draft")

    def test_two_steps_manager(self):
        self.user_employee.company_id.sudo().so_double_validation = "two_step"
        self.user_employee.company_id.sudo().so_double_validation_amount = 10
        so = (
            self.env["sale.order"]
            .with_user(self.user_manager)
            .create(
                {
                    "partner_id": self.partner_customer_usd.id,
                    "partner_invoice_id": self.partner_customer_usd.id,
                    "partner_shipping_id": self.partner_customer_usd.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": p.name,
                                "product_id": p.id,
                                "product_uom_qty": 2,
                                "product_uom": p.uom_id.id,
                                "price_unit": p.list_price,
                            },
                        )
                        for (_, p) in self.product_map.items()
                    ],
                    "pricelist_id": self.env.ref("product.list0").id,
                }
            )
        )
        # confirm quotation
        self.assertEqual(so.state, "draft")

    def test_two_steps_limit(self):
        so_double_validation_amount = sum(
            [2 * p.list_price for (k, p) in self.product_map.items()]
        )
        self.user_employee.company_id.sudo().so_double_validation = "two_step"
        self.user_employee.company_id.sudo().so_double_validation_amount = (
            so_double_validation_amount
        )

        so_total_price = sum([2 * p.list_price for (_, p) in self.product_map.items()])
        self.assertEqual(so_double_validation_amount, so_total_price)

        # create quotation
        so = self.create_so_by_user_employee()

        # test float compare with currency rounding
        compare_amount = (
            float_compare(
                so_double_validation_amount,
                so_total_price,
                precision_rounding=so.currency_id.rounding,
            )
            <= 0
        )
        self.assertEqual(compare_amount, True)

        # batch of condition tests, to set the SO state to `to_approve`
        self.assertEqual(so.company_id.so_double_validation, "two_step")
        self.assertFalse(self.user_employee.has_group("sales_team.group_sale_manager"))
        # self.assertTrue(so.is_amount_to_approve()) #TODO: FIX ME

        # state must be set to `to_approve` if condition above is satisfied
        # state = "to_approve"
        # self.assertEqual(so.state, state)  #TODO: FIX ME

    def test_two_steps_above_limit(self):
        self.user_employee.company_id.sudo().so_double_validation = "two_step"
        self.user_employee.company_id.sudo().so_double_validation_amount = 10
        # create quotation
        so = self.create_so_by_user_employee()
        # confirm quotation
        self.assertEqual(so.state, "to_approve")
        so.with_user(self.user_manager).action_approve()
        self.assertEqual(so.state, "draft")

    def test_confirm_so_above_limit_with_user_employee(self):
        self.user_employee.company_id.sudo().so_double_validation = "two_step"
        self.user_employee.company_id.sudo().so_double_validation_amount = 10
        # create quotation
        so = self.create_so_by_user_employee()
        # confirm quotation
        self.assertEqual(so.state, "to_approve")
        so.with_user(self.user_manager).action_approve()
        so.with_user(self.user_employee).action_confirm()
        self.assertEqual(so.state, "sale")

    def create_so_by_user_employee(self):
        so = (
            self.env["sale.order"]
            .with_user(self.user_employee)
            .create(
                {
                    "partner_id": self.partner_customer_usd.id,
                    "partner_invoice_id": self.partner_customer_usd.id,
                    "partner_shipping_id": self.partner_customer_usd.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": p.name,
                                "product_id": p.id,
                                "product_uom_qty": 2,
                                "product_uom": p.uom_id.id,
                                "price_unit": p.list_price,
                            },
                        )
                        for (_, p) in self.product_map.items()
                    ],
                    "pricelist_id": self.env.ref("product.list0").id,
                }
            )
        )
        return so
