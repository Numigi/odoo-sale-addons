# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestWebsiteSaleRequestPrice(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mail_template = cls.env["mail.template"].create(
            {"name": "mail template", "model_id": cls.env.ref("crm.model_crm_lead").id}
        )
        cls.sale_team = cls.env["crm.team"].create({"name": "team"})
        cls.env["ir.config_parameter"].create(
            [
                {"key": "website_sale_request_price", "value": True},
                {"key": "website_sale_request_price_threshold", "value": 500},
                {
                    "key": "website_sale_request_price_mail_template",
                    "value": cls.mail_template.id,
                },
                {
                    "key": "website_sale_request_price_sales_team",
                    "value": cls.sale_team.id,
                },
            ]
        )
        cls.lead_env = cls.env["crm.lead"]
        cls.brand = cls.env["product.brand"].create({"name": "brand A"})
        cls.product_template = cls.env["product.template"].create(
            {"name": "product A", "product_brand_id": cls.brand.id, "list_price": 1000}
        )
        cls.product = cls.product_template.product_variant_ids[0]

    def test_create_website_sale_request__check_product(self):
        self.product_template.list_price = 0
        self.assertFalse(self.product_template.is_request_price_required())
        self.product_template.list_price = 500
        self.assertTrue(self.product_template.is_request_price_required())
        self.product_template.list_price = 1000
        self.assertTrue(self.product_template.is_request_price_required())

    def test_create_website_sale_request__flow(self):
        post = {"product_product_id": self.product.id, "additional_information": "INFO"}
        self.lead_env.create_website_sale_request(post)
        lead = self.lead_env.search(
            [
                ("name", "=", "Shop: product A"),
                ("type", "=", "opportunity"),
                ("team_id", "=", self.sale_team.id),
                ("description", "=", post["additional_information"]),
                ("brand_ids", "=", self.brand.id),
                ("lead_line_ids.product_id", "=", self.product.id),
                ("lead_line_ids.name", "=", self.product.name),
                ("lead_line_ids.product_qty", "=", 1),
            ],
            limit=1,
        )
        self.assertEquals(len(lead), 1)
        mail = self.env["mail.mail"].search([("res_id", "=", lead.id)])
        self.assertEquals(len(mail), 1)
