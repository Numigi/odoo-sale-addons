# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestIntercoService(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.discount = 20

        cls.mother_company = cls.env["res.company"].create(
            {"name": "Mother Company", "interco_service_discount": cls.discount}
        )
        cls.subsidiary = cls.env["res.company"].create({"name": "Subsidiary"})
        cls.subsidiary_partner = cls.subsidiary.partner_id

        cls.interco_position = cls.env["account.fiscal.position"].create(
            {"name": "Interco Fiscal Position"}
        )
        cls.subsidiary_partner.fiscal_position_id = cls.interco_position

        cls.customer_position = cls.env["account.fiscal.position"].create(
            {"name": "Customer's Fiscal Position"}
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "My Customer",
                "company_id": None,
                "fiscal_position_id": cls.customer_position.id,
            }
        )
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

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "partner_invoice_id": cls.subsidiary.partner_id.id,
                "partner_shipping_id": cls.delivery_address.id,
                "is_interco_service": True,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

        cls.wizard = cls.env["sale.interco.service.invoice"].create(
            {"order_id": cls.order.id}
        )

    def test_wizard_fields(self):
        assert self.wizard.company_id == self.mother_company

        assert self.wizard.interco_company_id == self.subsidiary
        assert self.wizard.interco_partner_id == self.subsidiary_partner
        assert self.wizard.interco_position_id == self.interco_position
        assert self.wizard.discount == self.discount

        assert self.wizard.customer_id == self.customer
        assert self.wizard.customer_position == self.customer_position.display_name
        assert self.wizard.customer_delivery_address_id == self.delivery_address

    def test_fiscal_position_from_delivery_address(self):
        self.customer.fiscal_position_id = None
        self.delivery_address.fiscal_position_id = self.customer_position
        assert self.wizard.customer_position == self.customer_position.display_name

    def test_no_fiscal_position_defined(self):
        self.customer.fiscal_position_id = None
        assert not self.wizard.customer_position
