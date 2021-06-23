# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCommissionCase
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
        self.target.compute()
        assert self.target.base_amount == 5000

    def test_multiple_base_amount(self):
        invoice = self._create_invoice(amount=5000)
        self.target.compute()
        assert self.target.base_amount == 10000

    def test_different_currency_base_amount(self):
        cad_invoice = self._create_invoice(
            currency=self.env.ref("base.CAD"), amount=5000
        )
        self.target.compute()
        assert self.target.base_amount == 5000 + 5000 / self.exchange_rate_cad.rate

    def test_included_tags(self):
        self.category.included_tag_ids = self.included_tag

        self.invoice.invoice_line_ids.analytic_tag_ids = self.included_tag

        excluded_invoice = self._create_invoice(amount=5000)

        self.target.compute()
        assert self.target.base_amount == 5000

    def test_excluded_tags(self):
        self.category.excluded_tag_ids = self.excluded_tag

        self.invoice.invoice_line_ids.analytic_tag_ids = self.excluded_tag

        self.target.compute()
        assert not self.target.base_amount

    def test_included_excluded_tags(self):
        self.category.included_tag_ids = self.included_tag
        self.category.excluded_tag_ids = self.excluded_tag

        self.invoice.invoice_line_ids.analytic_tag_ids = self.included_tag

        excluded_invoice = self._create_invoice(amount=5000)
        excluded_invoice.invoice_line_ids.analytic_tag_ids = (
            self.included_tag | self.excluded_tag
        )

        self.target.compute()
        assert self.target.base_amount == 5000

    def test_new_personal_category_spreads_rates(self):
        self.target.fixed_rate = 0
        new_category = self.env["commission.category"].create(
            {
                "name": "New",
                "rate_type": "fixed",
                "basis": "my_sales",
                "fixed_rate": 0.5
            }
        )
        self.target.category_id = new_category
        self.target.onchange_category_id()

        assert self.target.fixed_rate == 0.5

    def test_date_range_onchange(self):
        new_date_range = self._create_date_range(
            "Q4", date(2024, 8, 17), date(2024, 11, 17)
        )

        self.target.date_range_id = new_date_range
        self.target.onchange_date_range()

        assert self.target.date_start == date(2024, 8, 17)
        assert self.target.date_end == date(2024, 11, 17)