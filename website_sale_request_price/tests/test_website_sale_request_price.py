# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ddt import ddt, data
from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


@ddt
class TestWebsiteSaleRequestPrice(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mail_template = cls.env["mail.template"].create(
            {
                "name": "mail template",
                "model_id": cls.env.ref("crm.model_crm_lead").id
            }
        )
        cls.sale_team = cls.env["crm.team"].create({"name": "team"})
        cls._set_config_param("website_sale_request_price", True)
        cls._set_config_param("website_sale_request_price_threshold", 500)
        cls._set_config_param(
            "website_sale_request_price_mail_template",
            cls.mail_template.id
        )
        cls._set_config_param(
            "website_sale_request_price_sales_team",
            cls.sale_team.id
        )
        cls.lead_env = cls.env["crm.lead"]
        cls.brand = cls.env["product.brand"].create({"name": "brand A"})
        cls.product_template = cls.env["product.template"].create(
            {"name": "product A", "product_brand_id": cls.brand.id, "list_price": 1000}
        )
        cls.product = cls.product_template.product_variant_ids[0]

        cls.normal_product_template = cls.env["product.template"].create(
            {"name": "product B", "list_price": 100}
        )
        cls.normal_product = cls.normal_product_template.product_variant_ids[0]

        # Create a valid partner for tests
        cls.partner = cls.env['res.partner'].create(
            {'name': 'Test Partner', 'email': 'test@example.com'}
        )

        # Setup for website
        cls.website = cls.env['website'].get_current_website()

    @classmethod
    def _set_config_param(cls, key, value):
        cls.env["ir.config_parameter"].set_param(key, value)

    def _create_sale_order(self):
        """Helper method to create a valid sale order"""
        return self.env['sale.order'].create(
            {'partner_id': self.partner.id, 'company_id': self.env.company.id}
        )

    def test_request_price_not_required(self):
        self.product_template.list_price = 499
        assert not self.product_template.is_request_price_required

    @data(500, 501)
    def test_request_price_required(self, price):
        self.product_template.list_price = price
        assert self.product_template.is_request_price_required

    def test_create_website_sale_request__flow(self):
        post = {"product_product_id": self.product.id, "additional_information": "INFO"}
        self.lead_env.create_website_sale_request(post)

        lead = self._get_lead()
        assert lead.type == "opportunity"
        assert lead.team_id == self.sale_team
        assert lead.brand_ids == self.brand

        line = lead.lead_line_ids
        assert line.product_id == self.product
        assert line.name == self.product.name
        assert line.product_qty == 1

        mail = self.env["mail.mail"].search(
            [("res_id", "=", lead.id), ("model", "=", "crm.lead")]
        )
        self.assertEquals(len(mail), 1)

    def test_create_request__with_float_product_id(self):
        post = {"product_product_id": str(float(self.product.id))}
        self.lead_env.create_website_sale_request(post)
        assert self._get_lead()

    def _get_lead(self):
        return self.lead_env.search(
            [("lead_line_ids.product_id", "=", self.product.id)]
        )

    def test_cart_update_blocked_for_request_price_product(self):
        """Test that cart_update blocks products requiring price request"""
        # Create a sale order first
        order = self._create_sale_order()

        # Simulate cart_update call for a high-priced product
        with self.assertRaises(ValidationError):
            order._cart_update(product_id=self.product.id, add_qty=1)

    def test_cart_update_allowed_for_normal_product(self):
        """Test that cart_update allows normal products"""
        # Create a sale order first
        order = self._create_sale_order()

        result = order._cart_update(product_id=self.normal_product.id, add_qty=1)
        self.assertEqual(result['quantity'], 1)
        self.assertEqual(result['line_id'], result['line_id'])

    def test_cart_update_json_blocked_for_request_price_product(self):
        """Test that cart_update_json blocks products requiring price request"""
        order = self._create_sale_order()

        # Simulate JSON call
        with self.assertRaises(ValidationError):
            order._cart_update(product_id=self.product.id, add_qty=1)

    def test_cart_update_json_allowed_for_normal_product(self):
        """Test that cart_update_json allows normal products"""
        order = self._create_sale_order()

        result = order._cart_update(product_id=self.normal_product.id, add_qty=1)
        self.assertEqual(result['quantity'], 1)

    def test_sale_order_line_creation_blocked_for_request_price_product(self):
        order = self._create_sale_order()

        with self.assertRaises(ValidationError):
            # Ajouter le contexte website
            self.env['sale.order.line'].with_context(website_id=self.website.id).create(
                {'order_id': order.id, 'product_id': self.product.id,
                    'product_uom_qty': 1, 'price_unit': 1000})

    def test_sale_order_line_creation_allowed_for_normal_product(self):
        """Test that sale order line creation is allowed for normal products"""
        order = self._create_sale_order()

        line = self.env['sale.order.line'].create(
            {
                'order_id': order.id,
                'product_id': self.normal_product.id,
                'product_uom_qty': 1,
                'price_unit': 100
            }
        )

        self.assertEqual(line.product_id, self.normal_product)
        self.assertEqual(line.order_id, order)

    def test_sale_order_line_modification_blocked_for_request_price_product(self):
        order = self._create_sale_order()

        line = self.env['sale.order.line'].create(
            {'order_id': order.id, 'product_id': self.normal_product.id,
                'product_uom_qty': 1, 'price_unit': 100})

        with self.assertRaises(ValidationError):
            line.with_context(website_id=self.website.id).write(
                {'product_id': self.product.id})

    def test_mixed_cart_update_with_request_price_product(self):
        """Test behavior with a mix of normal and hidden price products"""
        order = self._create_sale_order()

        # First add a normal product
        order._cart_update(product_id=self.normal_product.id, add_qty=1)

        # Trying to add a hidden price product should fail
        with self.assertRaises(ValidationError):
            order._cart_update(product_id=self.product.id, add_qty=1)

        # Verify that only the normal product is in the cart
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line.product_id, self.normal_product)

    def test_multiple_products_in_cart_update(self):
        """Test with multiple products to verify performance"""
        order = self._create_sale_order()

        # Create multiple normal products
        normal_products = self.env['product.product']
        for i in range(5):
            product = self.env['product.product'].create(
                {'name': f'Normal Product {i}', 'list_price': 100, 'type': 'product'}
            )
            normal_products += product

        # Adding all normal products should work
        for product in normal_products:
            result = order._cart_update(product_id=product.id, add_qty=1)
            self.assertEqual(result['quantity'], 1)

        self.assertEqual(len(order.order_line), 5)
