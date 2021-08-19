# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestCRMAssignByArea(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls.env.ref("base.main_partner")
        cls.tax_20 = cls.env["account.tax"].create({"name": "Tax 20%", "amount": 20})
        cls.tax_30 = cls.env["account.tax"].create({"name": "Tax 30%", "amount": 30})
        cls.product = cls.env["product.product"].create({"name": "Product"})

    def test_sale_order_no_default_taxes(self):
        self.company.account_sale_tax_id = False
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.partner
            with form.order_line.new() as line:
                line.product_id = self.product
            so = form.save()
            self.assertTrue(not so.order_line.tax_id)

    def test_sale_order_default_taxes_from_company(self):
        self.company.account_sale_tax_id = self.tax_20
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.partner
            with form.order_line.new() as line:
                line.product_id = self.product
            so = form.save()
            self.assertEqual(so.order_line.tax_id, self.tax_20)

    def test_sale_order_default_taxes_from_product(self):
        self.company.account_sale_tax_id = self.tax_20
        self.product.write({"taxes_id": [(6, 0, [self.tax_30.id])]})
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.partner
            with form.order_line.new() as line:
                line.product_id = self.product
            so = form.save()
            self.assertEqual(so.order_line.tax_id, self.tax_30)
