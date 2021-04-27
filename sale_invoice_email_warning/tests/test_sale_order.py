# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "My Customer"})
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "invoice_partner_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

    def test_email_not_defined(self):
        assert self.order.show_invoice_email_warning

    def test_email_defined(self):
        self.partner.email = "test123@example.com"
        assert not self.order.show_invoice_email_warning
