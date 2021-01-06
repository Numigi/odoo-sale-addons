# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestDeliveredQty(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.ref("base.user_demo")
        cls.company_1 = cls.env["res.company"].create({"name": "Company 1"})
        cls.company_2 = cls.env["res.company"].create({"name": "Company 2"})
        cls.customer = cls.env["res.partner"].create(
            {"name": "My Customer", "is_company": True, "customer": True}
        )
        cls.contact = cls.env["res.partner"].create(
            {"name": "My Contact", "parent_id": cls.customer.id}
        )

    def setUp(self):
        super().setUp()
        self.order = (
            self.env["sale.order"]
            .sudo(self.user)
            .new({"partner_id": self.customer.id, "company_id": self.company_1.id})
        )

    def test_no_restriction(self):
        self._trigger_partner_onchange()
        assert self.order.partner_id

    def test_not_allowed(self):
        self.customer.sale_authorized_company_ids = self.company_2
        res = self._trigger_partner_onchange()
        assert not self.order.partner_id
        assert "warning" in res

    def test_customer_allowed(self):
        self.customer.sale_authorized_company_ids = self.company_1
        self._trigger_partner_onchange()
        assert self.order.partner_id

    def test_contact_of_customer_not_allowed(self):
        self.customer.sale_authorized_company_ids = self.company_2
        self.order.partner_id = self.contact
        self._trigger_partner_onchange()
        assert not self.order.partner_id

    def test_contact_of_customer_allowed(self):
        self.customer.sale_authorized_company_ids = self.company_1
        self.order.partner_id = self.contact
        self._trigger_partner_onchange()
        assert self.order.partner_id

    def _trigger_partner_onchange(self):
        company = self.order.company_id
        self.user.write(
            {"company_ids": [(6, 0, [company.id])], "company_id": company.id}
        )
        return self.order._check_partner_authorized_companies()
