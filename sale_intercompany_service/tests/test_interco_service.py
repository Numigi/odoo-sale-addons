# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class IntercoServiceCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.interco_discount = 20

        cls.mother_company = cls._create_company("Mother Company")
        cls.mother_company.interco_service_discount = cls.interco_discount
        cls.mother_partner = cls.mother_company.partner_id

        cls.subsidiary = cls._create_company("Subsidiary")
        cls.subsidiary_partner = cls.subsidiary.partner_id

        cls.interco_position = cls._get_fiscal_position(cls.mother_company, "Ontario")
        cls._set_fiscal_position(
            cls.subsidiary_partner, cls.mother_company, cls.interco_position
        )

        cls.mother_position = cls._get_fiscal_position(cls.subsidiary, "Quebec")
        cls._set_fiscal_position(
            cls.mother_partner, cls.subsidiary, cls.mother_position
        )

        cls.customer_position = cls._get_fiscal_position(cls.subsidiary, "Manitoba")
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

        cls.product.taxes_id = cls._get_customer_tax(cls.mother_company, "HST 15%")
        cls.product.taxes_id |= cls._get_customer_tax(cls.subsidiary, "HST 13%")
        cls.product.supplier_taxes_id = cls._get_supplier_tax(cls.subsidiary, "HST 13%")

        cls.user = cls.env.ref("base.user_demo")
        cls.user.groups_id = cls.env.ref("sales_team.group_sale_salesman_all_leads")
        cls._set_user_company(cls.mother_company)
        cls.env = cls.env(user=cls.user)

        cls.order_line_name = "Order Line Description"
        cls.price_unit = 200
        cls.quantity = 15

        cls.order = cls.env["sale.order"].create(
            {
                "company_id": cls.mother_company.id,
                "partner_id": cls.customer.id,
                "partner_invoice_id": cls.subsidiary.partner_id.id,
                "partner_shipping_id": cls.delivery_address.id,
                "fiscal_position_id": cls.interco_position.id,
                "is_interco_service": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.order_line_name,
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "product_uom_qty": cls.quantity,
                            "price_unit": cls.price_unit,
                        },
                    )
                ],
            }
        )
        cls.order_line = cls.order.order_line
        cls.order_line.discount = 10
        cls.order_line._compute_tax_id()

        action = cls.order.open_interco_service_invoice_wizard()
        cls.wizard_obj = cls.env["sale.interco.service.invoice"]
        cls.wizard = cls.wizard_obj.browse(action["res_id"])

    @staticmethod
    def _get_customer_tax(company, tax_description):
        tax = (
            company.env["account.tax"]
            .sudo()
            .search(
                [
                    ("description", "ilike", tax_description),
                    ("company_id", "=", company.id),
                    ("type_tax_use", "=", "sale"),
                ],
                limit=1,
            )
        )
        assert tax
        return tax

    @staticmethod
    def _get_supplier_tax(company, tax_description):
        tax = (
            company.env["account.tax"]
            .sudo()
            .search(
                [
                    ("description", "ilike", tax_description),
                    ("company_id", "=", company.id),
                    ("type_tax_use", "=", "purchase"),
                ],
                limit=1,
            )
        )
        assert tax
        return tax

    @staticmethod
    def _get_fiscal_position(company, position_name):
        position = (
            company.env["account.fiscal.position"]
            .sudo()
            .search(
                [("name", "ilike", position_name), ("company_id", "=", company.id)],
                limit=1,
            )
        )
        assert position
        return position

    @staticmethod
    def _set_fiscal_position(partner, company, position):
        partner.with_context(
            force_company=company.id
        ).property_account_position_id = position

    @classmethod
    def _create_company(cls, name):
        company = cls.env["res.company"].create({"name": name})
        company.partner_id.company_id = False
        cls.env.user.company_ids |= company
        cls.env.user.company_id = company
        account_chart = cls.env.ref("l10n_ca.ca_en_chart_template_en")
        account_chart.try_loading_for_current_company()
        return company

    @classmethod
    def _set_user_company(cls, company):
        cls.user.sudo().write(
            {"company_id": company.id, "company_ids": [(6, 0, [company.id])]}
        )


class TestWizard(IntercoServiceCase):
    def test_wizard_fields(self):
        assert self.wizard.mode == "invoice"

        assert self.wizard.company_id == self.mother_company
        assert self.wizard.supplier_position_id == self.mother_position
        assert self.wizard.supplier_position_name == self.mother_position.display_name

        assert self.wizard.interco_company_id == self.subsidiary
        assert self.wizard.interco_partner_id == self.subsidiary_partner
        assert self.wizard.interco_position_id == self.interco_position
        assert self.wizard.interco_position_name == self.interco_position.display_name
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


class TestSaleOrderConstraints(IntercoServiceCase):
    def test_non_interco_partner(self):
        with pytest.raises(ValidationError):
            self.order.partner_invoice_id = self.customer

    def test_invoicing_address_not_shared_between_companies(self):
        self.subsidiary_partner.company_id = self.mother_company
        with pytest.raises(ValidationError):
            self.order.partner_invoice_id = self.subsidiary_partner

    def test_customer_not_shared_between_companies(self):
        self.customer.company_id = self.mother_company
        with pytest.raises(ValidationError):
            self.order.partner_id = self.customer

    def test_delivery_address_not_shared_between_companies(self):
        self.delivery_address.company_id = self.mother_company
        with pytest.raises(ValidationError):
            self.order.partner_shipping_id = self.delivery_address

    def test_product_not_shared_between_companies(self):
        self.product.company_id = self.mother_company
        with pytest.raises(ValidationError):
            self.order_line.product_id = self.product


class TestIntercoInvoices(IntercoServiceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order.action_confirm()
        cls.wizard.validate()

        cls.invoice_line = cls.order_line.invoice_lines
        cls.invoice = cls.invoice_line.invoice_id

        cls.supplier_invoice = cls.invoice.sudo().interco_supplier_invoice_id
        cls.supplier_invoice_line = cls.supplier_invoice.invoice_line_ids

        cls.customer_invoice = cls.invoice.sudo().interco_customer_invoice_id
        cls.customer_invoice_line = cls.customer_invoice.invoice_line_ids

    def test_interco_invoice_tax_amount_not_matching(self):
        self.invoice.tax_line_ids[0].amount += 0.01
        self.invoice.invoice_line_ids[0].price_unit -= 0.01
        with pytest.raises(ValidationError):
            self._validate_invoice(self.invoice)

    def test_supplier_invoice_tax_amount_not_matching(self):
        self.supplier_invoice.tax_line_ids[0].amount += 0.01
        self.supplier_invoice.invoice_line_ids[0].price_unit -= 0.01
        with pytest.raises(ValidationError):
            self._validate_invoice(self.supplier_invoice)

    def test_interco_invoice_price_not_matching(self):
        self.invoice.invoice_line_ids[0].price_unit += 0.01
        with pytest.raises(ValidationError):
            self._validate_invoice(self.invoice)

    def test_supplier_invoice_price_not_matching(self):
        self.supplier_invoice.invoice_line_ids[0].price_unit += 0.01
        with pytest.raises(ValidationError):
            self._validate_invoice(self.supplier_invoice)

    def test_interco_invoice_tax_amount_matching(self):
        self._validate_invoice(self.invoice)

    def test_customer_invoice_does_not_need_to_match_amounts(self):
        self._validate_invoice(self.customer_invoice)

    def _validate_invoice(self, invoice):
        self._set_user_company(invoice.company_id)
        self.user.groups_id |= self.env.ref("account.group_account_user")
        invoice.sudo(self.user).action_invoice_open()

    def test_interco_invoice(self):
        assert self.invoice.is_interco_service
        assert self.invoice.partner_id == self.subsidiary_partner
        assert self.invoice.partner_shipping_id == self.subsidiary_partner
        assert self.invoice.fiscal_position_id == self.interco_position
        assert self.invoice.company_id == self.mother_company
        assert self.invoice.account_id.company_id == self.mother_company
        assert self.invoice.journal_id.company_id == self.mother_company
        assert self.invoice.amount_tax

    def test_interco_invoice_line(self):
        # The interco discount is added to the customer discount
        assert self.invoice_line.discount == 28  # 100 * (1 - (1 - 10%) * (1 - 20%))
        assert self.invoice_line.account_id.company_id == self.mother_company

        tax = self.invoice_line.invoice_line_tax_ids
        assert tax.company_id == self.mother_company
        assert tax.name == "HST for sales - 13%"

    def test_interco_supplier_invoice(self):
        invoice = self.supplier_invoice
        assert invoice.is_interco_service
        assert invoice.partner_id == self.mother_partner
        assert invoice.type == "in_invoice"
        assert invoice.fiscal_position_id == self.mother_position
        assert invoice.company_id == self.subsidiary
        assert invoice.journal_id.company_id == self.subsidiary
        assert invoice.account_id.internal_type == "payable"
        assert invoice.account_id.company_id == self.subsidiary
        assert invoice.amount_tax

    def test_interco_supplier_invoice_line(self):
        line = self.supplier_invoice_line
        assert line.name == self.order_line_name
        assert line.product_id == self.product
        assert line.uom_id == self.product.uom_id
        assert line.quantity == self.quantity
        assert line.discount == self.invoice_line.discount
        assert line.price_unit == self.price_unit
        assert line.account_id.company_id == self.subsidiary

        tax = line.invoice_line_tax_ids
        assert tax.company_id == self.subsidiary
        assert tax.name == "HST for purchases - 13%"

    def test_interco_customer_invoice(self):
        invoice = self.customer_invoice
        assert invoice.is_interco_service
        assert invoice.partner_id == self.customer
        assert invoice.type == "out_invoice"
        assert invoice.fiscal_position_id == self.customer_position
        assert invoice.company_id == self.subsidiary
        assert invoice.journal_id.company_id == self.subsidiary
        assert invoice.account_id.internal_type == "receivable"
        assert invoice.account_id.company_id == self.subsidiary
        assert invoice.partner_shipping_id == self.delivery_address
        assert invoice.amount_tax

    def test_interco_customer_invoice_line(self):
        line = self.customer_invoice_line
        assert line.name == self.order_line_name
        assert line.product_id == self.product
        assert line.uom_id == self.product.uom_id
        assert line.quantity == self.quantity
        assert line.discount == 10  # discount defined on sale order line
        assert line.price_unit == self.price_unit
        assert line.account_id.company_id == self.subsidiary

        tax = line.invoice_line_tax_ids
        assert tax.company_id == self.subsidiary
        assert tax.name == "GST for sales - 5%"

    def test_summary_from_customer_invoice(self):
        self._set_user_company(self.subsidiary)
        wizard = self._open_summary_from_invoice(self.customer_invoice)
        assert wizard.mode == "summary"
        self._check_summary_fields(wizard)

    def test_summary_from_supplier_invoice(self):
        self._set_user_company(self.subsidiary)
        wizard = self._open_summary_from_invoice(self.supplier_invoice)
        assert wizard.mode == "summary"
        self._check_summary_fields(wizard)

    def test_summary_from_mother_invoice(self):
        self._set_user_company(self.mother_company)
        wizard = self._open_summary_from_invoice(self.invoice)
        assert wizard.mode == "summary"
        self._check_summary_fields(wizard)

    def test_summary_from_sale_order(self):
        self._set_user_company(self.mother_company)
        wizard = self._open_summary_from_invoice(self.invoice)
        assert wizard.mode == "summary"
        self._check_summary_fields(wizard)

    def _check_summary_fields(self, wizard):
        assert wizard.order_id == self.order
        assert wizard.order_name == self.order.sudo().display_name
        assert wizard.interco_invoice_ids == self.invoice
        assert wizard.interco_invoice_names == self.invoice.sudo().display_name
        assert wizard.supplier_invoice_ids == self.supplier_invoice
        assert (
            wizard.supplier_invoice_names == self.supplier_invoice.sudo().display_name
        )
        assert wizard.customer_invoice_ids == self.customer_invoice
        assert (
            wizard.customer_invoice_names == self.customer_invoice.sudo().display_name
        )

    def _open_summary_from_invoice(self, invoice):
        action = invoice.sudo(self.user).open_interco_service_summary()
        return self.wizard_obj.browse(action["res_id"])
