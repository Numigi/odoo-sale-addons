# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from datetime import date


class TestCommissionCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.chart_template = cls.env.ref(
            "l10n_ca.ca_en_chart_template_en",
            raise_if_not_found=False
        )
        cls.company_data = cls.setup_company_data("Company_name_1")

        cls.company = cls.company_data["company"]

        cls.user = cls._create_user()
        cls.user.groups_id = cls.env.ref("commission.group_user")
        cls.employee = cls._create_employee(user=cls.user)

        cls.manager_user = cls._create_user(
            name="Manager", email="manager@testmail.com"
        )
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "product_a",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 1000.0,
                "standard_price": 800.0,
                "property_account_income_id": cls.company_data[
                    "default_account_revenue"
                ].id,
                "property_account_expense_id": cls.company_data[
                    "default_account_expense"
                ].id,
            }
        )
        cls.manager_user.groups_id = cls.env.ref("commission.group_manager")
        cls.manager = cls._create_employee(user=cls.manager_user)

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
                "name": "type-5",
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
                "company_id": cls.company.id,
            }
        )

    @classmethod
    def setup_company_data(cls, company_name, **kwargs):
        def search_account(company, chart_template, field_name, domain):
            template_code = chart_template[field_name].code
            domain = [("company_id", "=", company.id)] + domain

            account = None
            if template_code:
                account = cls.env["account.account"].search(
                    domain + [("code", "=like", template_code + "%")], limit=1
                )

            if not account:
                account = cls.env["account.account"].search(domain, limit=1)
            return account

        chart_template = cls.chart_template or cls.env.company.chart_template_id
        company = cls.env["res.company"].create(
            {
                "name": company_name,
                **kwargs,
            }
        )
        cls.env.user.company_ids |= company
        cls.env.user.company_id = company

        chart_template.try_loading(company=company)

        # The currency could be different after the installation of the chart template.
        if kwargs.get("currency_id"):
            company.write({"currency_id": kwargs["currency_id"]})

        return {
            "company": company,
            "currency": company.currency_id,
            "default_account_revenue": cls.env["account.account"].search(
                [
                    ("company_id", "=", company.id),
                    (
                        "user_type_id",
                        "=",
                        cls.env.ref("account.data_account_type_revenue").id,
                    ),
                ],
                limit=1,
            ),
            "default_account_expense": cls.env["account.account"].search(
                [
                    ("company_id", "=", company.id),
                    (
                        "user_type_id",
                        "=",
                        cls.env.ref("account.data_account_type_expenses").id,
                    ),
                ],
                limit=1,
            ),
            "default_account_receivable": search_account(
                company,
                chart_template,
                "property_account_receivable_id",
                [("user_type_id.type", "=", "receivable")],
            ),
            "default_account_payable": cls.env["account.account"].search(
                [
                    ("company_id", "=", company.id),
                    ("user_type_id.type", "=", "payable"),
                ],
                limit=1,
            ),
            "default_account_assets": cls.env["account.account"].search(
                [
                    ("company_id", "=", company.id),
                    (
                        "user_type_id",
                        "=",
                        cls.env.ref("account.data_account_type_current_assets").id,
                    ),
                ],
                limit=1,
            ),
            "default_account_tax_sale": company.account_sale_tax_id.mapped(
                "invoice_repartition_line_ids.account_id"
            ),
            "default_account_tax_purchase": company.account_purchase_tax_id.mapped(
                "invoice_repartition_line_ids.account_id"
            ),
            "default_journal_misc": cls.env["account.journal"].search(
                [("company_id", "=", company.id), ("type", "=", "general")], limit=1
            ),
            "default_journal_sale": cls.env["account.journal"].search(
                [("company_id", "=", company.id), ("type", "=", "sale")], limit=1
            ),
            "default_journal_purchase": cls.env["account.journal"].search(
                [("company_id", "=", company.id), ("type", "=", "purchase")], limit=1
            ),
            "default_journal_bank": cls.env["account.journal"].search(
                [("company_id", "=", company.id), ("type", "=", "bank")], limit=1
            ),
            "default_journal_cash": cls.env["account.journal"].search(
                [("company_id", "=", company.id), ("type", "=", "cash")], limit=1
            ),
            "default_tax_sale": company.account_sale_tax_id,
            "default_tax_purchase": company.account_purchase_tax_id,
        }

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
        cls,
        _date=date(2020, 6, 17),
        move_type="out_invoice",
        user=None,
        currency=None,
        amount=0,
    ):
        if not user:
            user = cls.user
        if not currency:
            currency = cls.env.ref("base.USD")

        # move = self.env['account.move'].create({
        #     'move_type': 'in_invoice',
        #     'partner_id': self.partner_a.id,
        #     'invoice_date': fields.Date.from_string('2019-01-01'),
        #     'currency_id': self.currency_data['currency'].id,
        #     'invoice_payment_term_id': self.pay_terms_a.id,
        #     'invoice_line_ids': [
        #         (0, None, self.product_line_vals_1),
        #         (0, None, self.product_line_vals_2),
        #     ]
        # })

        account_id = (
            cls.env["account.account"]
            .search(
                [
                    ("company_id", "=", cls.company.id),
                    ("internal_group", "=", "expense"),
                ],
                limit=1,
            )
            .id
        )
        invoice = cls.env["account.move"].create(
            [
                {
                    "company_id": cls.company.id,
                    "move_type": move_type,
                    "partner_id": cls.customer.id,
                    "invoice_user_id": user.id,
                    "invoice_date": _date,
                    "date": _date,
                    "currency_id": currency.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": cls.product_a.id,
                                "name": "testing",
                                "quantity": 1,
                                "price_unit": amount,
                                "account_id": account_id,
                            },
                        )
                    ],
                }
            ]
        )

        invoice.post()
        return invoice

    @classmethod
    def _create_team(cls, name, manager):
        return cls.env["crm.team"].create({"name": name, "user_id": manager.id})
