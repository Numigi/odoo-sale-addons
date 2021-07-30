# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from datetime import date


class TestCommissionCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls._create_company()

        cls.user = cls._create_user()
        cls.user.groups_id = cls.env.ref("commission.group_user")

        cls.employee = cls._create_employee(user=cls.user)

        cls.customer = cls.env["res.partner"].create({"name": "testing"})

        cls.category = cls._create_category("Standard")

        cls.exchange_rate_cad = cls.env["res.currency.rate"].create(
            {
                "name": date(2020, 6, 17),
                "rate": 0.8,
                "currency_id": cls.env.ref("base.CAD").id,
            }
        )

        cls.date_range_type = cls.env["date.range.type"].create(
            {
                "name": "type",
            }
        )

        cls.date_range = cls._create_date_range(
            "Q2", date(2020, 5, 17), date(2020, 7, 17)
        )

    @classmethod
    def _create_category(cls, name, basis="my_sales"):
        return cls.env["commission.category"].create(
            {
                "name": name,
                "basis": basis,
            }
        )

    @classmethod
    def _create_date_range(cls, name, date_start, date_end):
        return cls.env["date.range"].create(
            {
                "name": name,
                "date_start": date_start,
                "date_end": date_end,
                "type_id": cls.date_range_type.id,
            }
        )

    @classmethod
    def _create_target(
        cls,
        employee=None,
        category=None,
        target_amount=0,
        date_range=None,
        fixed_rate=0,
    ):
        if not employee:
            employee = cls.employee
        if not category:
            category = cls.category
        if not date_range:
            date_range = cls.date_range

        return cls.env["commission.target"].create(
            {
                "employee_id": employee.id,
                "category_id": category.id,
                "target_amount": target_amount,
                "date_range_id": date_range.id,
                "fixed_rate": fixed_rate,
                "date_start": date_range.date_start,
                "date_end": date_range.date_end,
            }
        )

    @classmethod
    def _create_company(cls, name="Testing"):
        company = cls.env["res.company"].create({"name": name})
        cls.env.user.company_ids |= company
        cls.env.user.company_id = company
        account_chart = cls.env.ref("l10n_generic_coa.configurable_chart_template")
        account_chart.try_loading_for_current_company()
        return company

    @classmethod
    def _create_user(cls, name="Testing", email="testing@testmail.com"):
        return cls.env["res.users"].create(
            {
                "name": name,
                "email": email,
                "login": name,
                "company_ids": [(4, cls.company.id)],
                "company_id": cls.company.id,
            }
        )

    @classmethod
    def _create_employee(cls, user=None):
        return cls.env["hr.employee"].create(
            {
                "name": user.name if user else "Some Employee",
                "user_id": user.id if user else None,
            }
        )

    @classmethod
    def _create_target_rate(cls, target, slice_from, slice_to, percentage=0):
        return cls.env["commission.target.rate"].create(
            {
                "target_id": target.id,
                "slice_from": slice_from,
                "slice_to": slice_to,
                "commission_percentage": percentage,
            }
        )

    @classmethod
    def _create_category_rate(cls, category, slice_from, slice_to, percentage=0):
        return cls.env["commission.category.rate"].create(
            {
                "category_id": category.id,
                "slice_from": slice_from,
                "slice_to": slice_to,
                "commission_percentage": percentage,
            }
        )

    @classmethod
    def _create_invoice(
        cls, _date=date(2020, 6, 17), user=None, currency=None, amount=0
    ):
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

    @classmethod
    def _create_department(cls, name, manager):
        return cls.env["hr.department"].create(
            {
                "name": name,
                "manager_id": manager.id,
            }
        )
