# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

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
