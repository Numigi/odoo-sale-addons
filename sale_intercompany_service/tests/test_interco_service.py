# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from .common import IntercoServiceCase


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


class TestOnchange(IntercoServiceCase):
    def setUp(self):
        super().setUp()
        self.order = self.env["sale.order"].new({})
        self.order.partner_id = self.customer

    def test_non_interco(self):
        self.order.onchange_partner_id()
        assert self.order.partner_invoice_id == self.customer
        assert self.order.partner_shipping_id == self.customer

    def test_interco(self):
        self.order.is_interco_service = True
        self.order.onchange_partner_id()
        assert not self.order.partner_invoice_id
        assert self.order.partner_shipping_id == self.customer

    def test_interco_with_invoice_address_selected(self):
        self.order.is_interco_service = True
        self.order.partner_invoice_id = self.subsidiary_partner
        self.order.onchange_partner_id()
        assert self.order.partner_invoice_id == self.subsidiary_partner
        assert self.order.partner_shipping_id == self.customer


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
        self.user.groups_id |= self.env.ref("account.group_account_invoice")
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
        assert not invoice.user_id

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
        assert not invoice.user_id

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


class TestIntercompanyAccounts(IntercoServiceCase):

    def test_intercompany_revenue_account(self):
        account = self._get_any_account(self.mother_company)
        product = self.product.with_context(force_company=self.mother_company.id)
        product.categ_id.intercompany_revenue_account_id = account

        self.order.action_confirm()
        self.wizard.validate()

        line = self._get_interco_invoice_line()
        assert line.account_id == account

    def test_final_customer_invoice_revenue_account(self):
        account = self._get_any_account(self.subsidiary)
        product = self.product.with_context(force_company=self.subsidiary.id)
        product.categ_id.intercompany_revenue_account_id = account

        self.order.action_confirm()
        self.wizard.validate()

        line = self._get_final_customer_invoice_line()
        assert line.account_id != account

    def test_intercompany_expense_account(self):
        account = self._get_any_account(self.subsidiary)
        product = self.product.with_context(force_company=self.subsidiary.id)
        product.categ_id.intercompany_expense_account_id = account

        self.order.action_confirm()
        self.wizard.validate()

        line = self._get_interco_supplier_invoice_line()
        assert line.account_id == account

    def _get_interco_supplier_invoice_line(self):
        invoice = self.order_line.invoice_lines.invoice_id
        supplier_invoice = invoice.sudo().interco_supplier_invoice_id
        return supplier_invoice.invoice_line_ids

    def _get_interco_invoice_line(self):
        invoice = self.order_line.invoice_lines.invoice_id
        return invoice.invoice_line_ids

    def _get_final_customer_invoice_line(self):
        invoice = self.order_line.invoice_lines.invoice_id
        customer_invoice = invoice.sudo().interco_customer_invoice_id
        return customer_invoice.invoice_line_ids

    def _get_any_account(self, company):
        return self.env["account.account"].sudo().search(
            [("company_id", "=", company.id)], limit=1
        )
