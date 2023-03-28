# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase
from datetime import date


class TestPayrollCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = cls.env["res.users"].create(
            {"name": "Test", "email": "testing@testmail.com", "login": "testing"}
        )

        cls.employee = cls.env["hr.employee"].create(
            {
                "name": cls.user.name,
                "user_id": cls.user.id,
            }
        )

        cls.customer = cls.env["res.partner"].create({"name": "testing"})

        cls.category = cls.env["commission.category"].create(
            {
                "name": "Testing",
                "basis": "my_sales",
            }
        )

        cls.date_start = date(2021, 1, 1)
        cls.date_middle = date(2021, 2, 15)
        cls.date_end = date(2021, 3, 30)
        cls.date_range_type = cls.env["date.range.type"].create(
            {
                "name": "type",
            }
        )
        cls.date_range = cls.env["date.range"].create(
            {
                "name": "Q1",
                "date_start": cls.date_start,
                "date_end": cls.date_end,
                "type_id": cls.date_range_type.id,
            }
        )

        cls.company = cls.env["res.company"].create({"name": "Testing"})
        cls.env.user.company_ids |= cls.company
        cls.env.user.company_id = cls.company
        account_chart = cls.env.ref("l10n_generic_coa.configurable_chart_template")
        account_chart.try_loading_for_current_company()

        cls.period = cls.env["payroll.period"].create(
            {
                "name": "Testing",
                "date_from": cls.date_start,
                "date_to": cls.date_end,
                "company_id": cls.company.id,
            }
        )

    @classmethod
    def _create_invoice(cls, _date=None, user=None, currency=None, amount=0):
        if not _date:
            _date = cls.date_middle
        if not user:
            user = cls.user
        if not currency:
            currency = cls.env.ref("base.USD")

        invoice = cls.env["account.invoice"].create(
            {
                "company_id": cls.company.id,
                "partner_id": cls.customer.id,
                "user_id": user.id,
                "date_invoice": _date,
                "currency_id": currency.id,
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
