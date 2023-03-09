# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestInvoice(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "My Customer"})
        cls.salesman = cls.env.ref("base.user_demo")
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "invoice_user_id": cls.salesman.id,
                "move_type": "out_invoice",
            }
        )

    def test_salesman_not_following(self):
        assert self.salesman.partner_id not in self.invoice.message_partner_ids
