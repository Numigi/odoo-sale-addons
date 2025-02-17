# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_order_type.tests.test_sale_order_type import TestSaleOrderType
from odoo.tests import tagged


@tagged("post_install")
class TestSaleOrderTypeTemplate(TestSaleOrderType):
    def setUp(self):
        super(TestSaleOrderTypeTemplate, self).setUp()
        values = {
            "name": "My Template",
            "subject": "My Subject",
            "body_html": "Template Body",
            "model_id": self.env.ref("sale.model_sale_order").id,
            "use_default_to": True,
        }
        self.template = self.env["mail.template"].create(values)

    def test_action_quotation_send_right_email_template(self):
        """
        Test that the right email template is used when sending a quotation.
        """
        order = self.create_sale_order()
        self.sale_type_route.mail_template = self.template.id
        order.type_id = self.sale_type_route.id
        order.onchange_type_id()
        action = order.action_quotation_send()
        self.assertEqual(
            action["context"]["default_use_template"],
            bool(order.type_id.mail_template.id),
        )
        self.assertEqual(
            action["context"]["default_template_id"],
            order.type_id.mail_template.id,
        )
