# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestInvoiceGrouping(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "invoice_policy": "order",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Lucas",
            }
        )

        cls.usd = cls.env.ref("base.USD")

        cls.first_sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "currency_id": cls.usd.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

        cls.first_sale_order_line = cls.env["sale.order.line"].create(
            {
                "product_id": cls.product.id,
                "order_id": cls.first_sale_order.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1,
                "name": "line",
                "price_unit": 100,
            }
        )

        cls.second_sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "currency_id": cls.usd.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

        cls.second_sale_order_line = cls.env["sale.order.line"].create(
            {
                "product_id": cls.product.id,
                "order_id": cls.second_sale_order.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1,
                "name": "line",
                "price_unit": 100,
            }
        )

        cls.first_sale_order.action_confirm()
        cls.second_sale_order.action_confirm()

        cls.grouped_sos = cls.first_sale_order | cls.second_sale_order

    def test_grouping_enabled(self):
        self.env["ir.config_parameter"].set_param(
            "sale_invoice_create_group_by_origin.config", "on"
        )

        self.grouped_sos._create_invoices(final=True)

        invoices = self.env["account.move"].search(
            [
                ("partner_id", "=", self.partner.id),
            ]
        )

        assert len(invoices) == 2

    def test_grouping_disabled(self):
        self.env["ir.config_parameter"].set_param(
            "sale_invoice_create_group_by_origin.config", "off"
        )

        self.grouped_sos._create_invoices(final=True)

        invoices = self.env["account.move"].search(
            [
                ("partner_id", "=", self.partner.id),
            ]
        )

        assert len(invoices) == 1
