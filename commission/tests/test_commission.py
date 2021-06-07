# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from datetime import date
from ddt import ddt, data

@ddt
class TestPayment(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = cls.env["res.users"].create(
            {"name": "testing", "email": "test@test.com", "login": "testing"}
        )

        cls.company = cls._create_company("testing")

        cls.customer = cls.env["res.partner"].create({"name": "testing"})

        cls.employee = cls.env["hr.employee"].create(
            {"name": "jean", "user_id": cls.user.id}
        )

        cls.category = cls.env["commission.category"].create(
            {
                "name": "standard",
            }
        )

        cls.target = cls.env["commission.target"].create(
            {
                "employee_id": cls.employee.id,
                "category_id": cls.category.id,
                "date_start": date(2020, 5, 17),
                "date_end": date(2020, 7, 17),
            }
        )

    @classmethod
    def _create_company(cls, name):
        company = cls.env["res.company"].create({"name": name})
        cls.env.user.company_ids |= company
        cls.env.user.company_id = company
        account_chart = cls.env.ref("l10n_generic_coa.configurable_chart_template")
        account_chart.try_loading_for_current_company()
        return company

    @classmethod
    def _create_invoice(cls, user=None, date_=None):
        invoice = cls.env["account.invoice"].create(
            {
                "company_id": cls.company.id,
                "partner_id": cls.customer.id,
                "user_id": user.id if user else cls.user.id,
                "date_invoice": date(2020, 6, 17) if not date_ else date_,
            }
        )
        line = cls.env["account.invoice.line"].create(
            {
                "name": "testing",
                "invoice_id": invoice.id,
                "quantity": 5,
                "price_unit": 1,
                "account_id": cls.env["account.account"]
                .search(
                    [
                        ("company_id", "=", cls.company.id),
                        ("internal_group", "=", "expense"),
                    ],
                    limit=1,
                )
                .id,
            }
        )
        invoice.action_invoice_open()
        return invoice

    def test_find_invoice_empty(self):
        invoices = self.target._find_invoices()
        assert invoices == self.env["account.invoice"]

    def test_find_invoice_single_user(self):
        invoice = self._create_invoice()
        invoices = self.target._find_invoices()
        assert invoice == invoices

    def test_find_invoice_wrong_user(self):
        self._create_invoice(user=self.env.ref("base.user_demo"))
        invoices = self.target._find_invoices()
        assert not invoices

    @data(date(2020, 5, 16), date(2020, 7, 18))
    def test_find_invoice_wrong_date(self, wrong_date):
        self._create_invoice(date_=wrong_date)
        invoices = self.target._find_invoices()
        assert not invoices

    @data(date(2020, 5, 17), date(2020, 7, 17))
    def test_find_invoice_correct_date(self, correct_date):
        invoice = self._create_invoice(date_=correct_date)
        invoices = self.target._find_invoices()
        assert invoice == invoices
