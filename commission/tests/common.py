# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from datetime import date


class TestCommissionCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = cls.env["res.users"].create(
            {"name": "testing", "email": "test@test.com", "login": "testing"}
        )

        cls.company = cls._create_company("testing")

        cls.customer = cls.env["res.partner"].create({"name": "testing"})

        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Jean",
                "user_id": cls.user.id,
            }
        )

        cls.category = cls.env["commission.category"].create(
            {
                "name": "standard",
            }
        )

        cls.exchange_rate_cad = cls.env["res.currency.rate"].create(
            {
                "name": date(2020, 6, 17),
                "rate": 0.8,
                "currency_id": cls.env.ref("base.CAD").id,
            }
        )

    @classmethod
    def _create_target(cls, employee, category, amount):
        return cls.env["commission.target"].create(
            {
                "employee_id": employee.id,
                "category_id": category.id,
                "date_start": date(2020, 5, 17),
                "date_end": date(2020, 7, 17),
                "target_amount": amount,
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
    def _create_rate(cls, slice_from, slice_to, percentage=0):
        return cls.env["commission.target.rate"].create(
            {
                "target_id": cls.target.id,
                "slice_from": slice_from,
                "slice_to": slice_to,
                "commission_percentage": percentage,
            }
        )

    @classmethod
    def _create_invoice(cls, user=None, date_=None, currency=None, amount=0):
        invoice = cls.env["account.invoice"].create(
            {
                "company_id": cls.company.id,
                "partner_id": cls.customer.id,
                "user_id": user.id if user else cls.user.id,
                "date_invoice": date(2020, 6, 17) if not date_ else date_,
                "currency_id": cls.env.ref(f"base.{currency}").id
                if currency
                else cls.env.ref("base.USD").id,
            }
        )
        cls.env["account.invoice.line"].create(
            {
                "name": "testing",
                "invoice_id": invoice.id,
                "quantity": 1,
                "price_unit": amount,
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
