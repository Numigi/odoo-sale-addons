# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytest
from .common import TestCommissionCase
from odoo.exceptions import AccessError
from datetime import date
from ddt import ddt, data


@ddt
class TestCommissionPersonal(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls._create_invoice(amount=5000)

        cls.target = cls._create_target(target_amount=100000)

        cls.included_tag = cls.env["account.analytic.tag"].create({"name": "Chairs"})

        cls.excluded_tag = cls.env["account.analytic.tag"].create({"name": "Tables"})

    def test_compute_show_invoices(self):
        assert self.target.show_invoices

    def test_compute_show_child_targets(self):
        assert not self.target.show_child_targets

    def test_view_invoice_lines(self):
        self.target.invoice_line_ids = self.invoice.invoice_line_ids
        action = self.target.view_invoice_lines()
        domain = action["domain"]
        lines = self.env["account.invoice.line"].search(domain)
        assert lines == self.invoice.invoice_line_ids

    def test_find_invoice_single_user(self):
        invoices = self.target._get_invoices()
        assert self.invoice == invoices

    def test_find_invoice_wrong_user(self):
        self.invoice.user_id = self.env.ref("base.user_demo")
        invoices = self.target._get_invoices()
        assert not invoices

    @data("in_invoice", "in_refund")
    def test_supplier_invoice(self, type_):
        self.invoice.type = type_
        invoices = self.target._get_invoices()
        assert not invoices

    @data("draft", "cancel")
    def test_excluded_state(self, state):
        self.invoice.state = state
        invoices = self.target._get_invoices()
        assert not invoices

    @data(date(2020, 5, 17), date(2020, 7, 17))
    def test_find_invoice_correct_date_range(self, correct_date):
        self.invoice.date_invoice = correct_date
        invoices = self.target._get_invoices()
        assert self.invoice == invoices

    @data(date(2020, 5, 16), date(2020, 7, 18))
    def test_find_invoice_wrong_date_range(self, wrong_date):
        self.invoice.date_invoice = wrong_date
        invoices = self.target._get_invoices()
        assert not invoices

    def test_base_amount(self):
        self._compute_target()
        assert self.target.invoiced_amount == 5000
        assert self.target.base_amount == 5000

    def test_multiple_base_amount(self):
        self._create_invoice(amount=5000)
        self._compute_target()
        assert self.target.base_amount == 10000

    def test_different_currency_base_amount(self):
        self._create_invoice(
            currency=self.env.ref("base.CAD"), amount=5000
        )
        self._compute_target()
        assert self.target.base_amount == 5000 + 5000 / self.exchange_rate_cad.rate

    def test_included_tags(self):
        self.category.included_tag_ids = self.included_tag

        self.invoice.invoice_line_ids.analytic_tag_ids = self.included_tag

        self._create_invoice(amount=5000)

        self._compute_target()
        assert self.target.base_amount == 5000

    def test_excluded_tags(self):
        self.category.excluded_tag_ids = self.excluded_tag

        self.invoice.invoice_line_ids.analytic_tag_ids = self.excluded_tag

        self._compute_target()
        assert not self.target.base_amount

    def test_included_excluded_tags(self):
        self.category.included_tag_ids = self.included_tag
        self.category.excluded_tag_ids = self.excluded_tag

        self.invoice.invoice_line_ids.analytic_tag_ids = self.included_tag

        excluded_invoice = self._create_invoice(amount=5000)
        excluded_invoice.invoice_line_ids.analytic_tag_ids = (
            self.included_tag | self.excluded_tag
        )

        self._compute_target()
        assert self.target.base_amount == 5000

    def test_new_personal_category_spreads_rates(self):
        self.target.fixed_rate = 0
        new_category = self.env["commission.category"].create(
            {
                "name": "New",
                "rate_type": "fixed",
                "basis": "my_sales",
                "fixed_rate": 0.5,
            }
        )
        self.target.category_id = new_category
        self.target.onchange_category_id()

        assert self.target.fixed_rate == 0.5

    def test_name_sequence(self):
        self.target.name = self.target._get_next_sequence_number()

        assert "CO" in self.target.name

    def test_name_sequence_new_company(self):
        new_company = self._create_company(name="New")
        new_sequence = self.env["ir.sequence"].search(
            [("code", "=", "commission.target.reference")]
        )
        new_sequence.prefix = "BO"
        new_sequence.company_id = new_company
        self.target.company_id = new_company
        self.target.name = self.target._get_next_sequence_number()

        assert "BO" in self.target.name

    def test_confirm_target_confirmed_state(self):
        self.target.set_confirmed_state()
        assert self.target.state == "confirmed"

    def test_done_method_done_state(self):
        self.target.set_done_state()
        assert self.target.state == "done"

    def test_cancel_method_cancel_state(self):
        self.target.set_cancelled_state()
        assert self.target.state == "cancelled"

    def test_draft_method_draft_state(self):
        self.target.set_draft_state()
        assert self.target.state == "draft"

    def test_compute_not_own_commission(self):
        self.target.employee_id = self._create_employee()
        with pytest.raises(AccessError):
            self._compute_target()

    def test_target_access_domain(self):
        targets = self._search_employee_targets()
        assert targets == self.target

    def test_target_access_domain__wrong_company(self):
        self.target.company_id = self._create_company(name="Wrong")
        targets = self._search_employee_targets()
        assert not targets

    def _compute_target(self):
        self.target.sudo(self.user).compute()

    def _search_employee_targets(self):
        domain = (
            self.env["commission.target"]
            .sudo(self.user)
            .get_extended_security_domain()
        )
        return self.env["commission.target"].search(domain)
