# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class IntercoServiceCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.interco_discount = 20

        cls.mother_company = cls._create_company("Mother Company")
        cls.mother_company.interco_service_discount = cls.interco_discount

        cls.subsidiary = cls._create_company("Subsidiary")
        cls.subsidiary_partner = cls.subsidiary.partner_id

        cls.interco_position = cls.env["account.fiscal.position"].create(
            {"name": "Interco Fiscal Position", "company_id": cls.mother_company.id}
        )
        cls._set_fiscal_position(
            cls.subsidiary_partner, cls.mother_company, cls.interco_position
        )

        cls.customer_position = cls.env["account.fiscal.position"].create(
            {"name": "Customer's Fiscal Position"}
        )
        cls.customer = cls.env["res.partner"].create(
            {"name": "My Customer", "company_id": None}
        )
        cls._set_fiscal_position(cls.customer, cls.subsidiary, cls.customer_position)

        cls.delivery_address = cls.env["res.partner"].create(
            {"name": "Delivery Address", "type": "delivery", "company_id": None}
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "My Product",
                "type": "service",
                "company_id": None,
                "invoice_policy": "order",
            }
        )

        cls.order = cls.env["sale.order"].create(
            {
                "company_id": cls.mother_company.id,
                "partner_id": cls.customer.id,
                "partner_invoice_id": cls.subsidiary.partner_id.id,
                "partner_shipping_id": cls.delivery_address.id,
                "is_interco_service": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        cls.order_line = cls.order.order_line
        cls.order_line.discount = 10

        cls.user = cls.env.ref("base.user_demo")
        cls.user.groups_id = cls.env.ref("sales_team.group_sale_salesman_all_leads")
        cls.user.write(
            {
                "company_id": cls.mother_company.id,
                "company_ids": [(6, 0, [cls.mother_company.id])],
            }
        )
        cls.env = cls.env(user=cls.user)

        cls.wizard = cls.env["sale.interco.service.invoice"].create(
            {"order_id": cls.order.id}
        )

    @staticmethod
    def _set_fiscal_position(partner, company, position):
        partner.with_context(
            force_company=company.id
        ).property_account_position_id = position

    @classmethod
    def _create_company(cls, name):
        account_chart = cls.env.ref("l10n_generic_coa.configurable_chart_template")
        company = cls.env["res.company"].create({"name": name})
        cls.env.user.company_ids |= company
        cls.env.user.company_id = company
        account_chart.try_loading_for_current_company()
        return company


class TestWizard(IntercoServiceCase):
    def test_wizard_fields(self):
        assert self.wizard.company_id == self.mother_company

        assert self.wizard.interco_company_id == self.subsidiary
        assert self.wizard.interco_partner_id == self.subsidiary_partner
        assert self.wizard.interco_position_id == self.interco_position
        assert self.wizard.discount == self.interco_discount

        assert self.wizard.customer_id == self.customer
        assert self.wizard.customer_position_id == self.customer_position
        assert self.wizard.customer_position_name == self.customer_position.display_name
        assert self.wizard.customer_delivery_address_id == self.delivery_address

    def test_fiscal_position_from_delivery_address(self):
        self._set_fiscal_position(self.customer, self.subsidiary, None)
        self._set_fiscal_position(
            self.delivery_address, self.subsidiary, self.customer_position
        )
        assert self.wizard.customer_position_id == self.customer_position

    def test_no_fiscal_position_defined(self):
        self._set_fiscal_position(self.customer, self.subsidiary, None)
        assert not self.wizard.customer_position_id


class TestIntercoInvoice(IntercoServiceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order.sudo(cls.user).action_confirm()
        cls.wizard.validate()

        cls.invoice_line = cls.order_line.invoice_lines
        cls.invoice = cls.invoice_line.invoice_id

    def test_invoice_fields(self):
        assert self.invoice.partner_id == self.subsidiary_partner
        assert self.invoice.partner_shipping_id == self.subsidiary_partner
        assert self.invoice.fiscal_position_id == self.interco_position

    def test_invoice_line_discount(self):
        # The interco discount is added to the customer discount
        assert self.invoice_line.discount == 28  # 100 * (1 - (1 - 10%) * (1 - 20%))
