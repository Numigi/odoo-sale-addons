# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.commission.tests.common import CommissionCase


class TestCommissionTarget(CommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.target = cls._create_target(target_amount=1)

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "william",
            }
        )

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

        cls.order_line = cls.env["sale.order.line"].create(
            {
                "product_id": cls.product.id,
                "order_id": cls.order.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1,
                "name": "line",
            }
        )

        cls.invoice = cls._create_invoice(amount=1)
        cls.invoice_line = cls.invoice.invoice_line_ids

    def test_standard_relation(self):
        self.order_line.invoice_lines = self.invoice.invoice_line_ids
        orders = self.target._get_related_sale_order(self.invoice_line)
        assert orders == self.order

    def test_get_related_intercompany_order(self):
        self.invoice.interco_service_order_id = self.order
        orders = self.target._get_related_sale_order(self.invoice_line)
        assert orders == self.order

    def test_final_customer_invoice(self):
        self.order.company_id = self._make_new_company()
        self.invoice.interco_service_order_id = self.order
        self.invoice.is_interco_service = True
        assert self.invoice in self.target._get_invoices()

    def test_intercompany_invoice(self):
        self.invoice.interco_service_order_id = self.order
        self.invoice.is_interco_service = True
        assert self.invoice not in self.target._get_invoices()

    def _make_new_company(self):
        return self.env["res.company"].create({"name": "New Company"})
