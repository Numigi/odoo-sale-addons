# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.product_configurator.tests import (
    test_product_configurator_test_cases as TC,
)


class ProductConfigSale(TC.ProductConfiguratorTestCases):
    def setUp(self):
        super(ProductConfigSale, self).setUp()
        self.SaleOrderId = self.env["sale.order"]
        self.productPricelist = self.env["product.pricelist"]
        self.currency_id = self.env.ref("base.USD")
        self.ProductConfWizard = self.env["product.configurator.sale"]
        self.user = self.env["res.users"].create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "name": "Salesman",
                "login": "Salesman",
                "email": "Salesman@test.com",
                "groups_id": [
                    (6, 0, [self.env.ref("sales_team.group_sale_salesman").id,
                            self.env.ref("purchase.group_purchase_user").id])
                ],
            }
        )
        self.resPartner = self.user.partner_id

    def test_00_access_reconfigure_product(self):
        pricelist_id = self.productPricelist.create(
            {
                "name": "Test Pricelist",
                "currency_id": self.currency_id.id,
            }
        )
        sale_order_id = self.SaleOrderId.with_user(self.user).create(
            {
                "partner_id": self.resPartner.id,
                "partner_invoice_id": self.resPartner.id,
                "partner_shipping_id": self.resPartner.id,
                "pricelist_id": pricelist_id.id,
            }
        )
        context = dict(
            default_order_id=sale_order_id.id,
            wizard_model="product.configurator.sale",
        )
        self.ProductConfWizard =\
            self.ProductConfWizard.with_user(self.user).with_context(context)
        sale_order_id.action_config_start()
        self._configure_product_nxt_step()
        sale_order_id.order_line.reconfigure_product()
