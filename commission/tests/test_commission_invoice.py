# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCommissionCase
from datetime import date
from ddt import ddt, data


@ddt
class TestCommissionInvoice(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls._create_invoice(amount=5000)

    def test_find_invoice_single_user(self):
        invoices = self.target._find_invoices()
        assert self.invoice == invoices

    def test_find_invoice_wrong_user(self):
        self.invoice.user_id = self.env.ref("base.user_demo")
        invoices = self.target._find_invoices()
        assert not invoices

    @data("in_invoice", "in_refund")
    def test_supplier_invoice(self, type_):
        self.invoice.type = type_
        invoices = self.target._find_invoices()
        assert not invoices

    @data("draft", "cancel")
    def test_excluded_state(self, state):
        self.invoice.state = state
        invoices = self.target._find_invoices()
        assert not invoices

    @data(date(2020, 5, 17), date(2020, 7, 17))
    def test_find_invoice_correct_date(self, correct_date):
        self.invoice.date_invoice = correct_date
        invoices = self.target._find_invoices()
        assert self.invoice == invoices

    @data(date(2020, 5, 16), date(2020, 7, 18))
    def test_find_invoice_wrong_date(self, wrong_date):
        self.invoice.date_invoice = wrong_date
        invoices = self.target._find_invoices()
        assert not invoices

    def test_invoiced_amount(self):
        self.target.compute()
        assert self.target.invoiced_amount == 5000

    def test_multiple_invoiced_amount(self):
        invoice = self._create_invoice(amount=5000)
        self.target.compute()
        assert self.target.invoiced_amount == 10000

    def test_different_currency_invoiced_amount(self):
        cad_invoice = self._create_invoice(currency="CAD", amount=5000)
        self.target.compute()
        assert self.target.invoiced_amount == 5000 + 5000 / self.exchange_rate_cad.rate
