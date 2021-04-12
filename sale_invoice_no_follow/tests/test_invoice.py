# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class IntercoCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "My Customer"})
        cls.salesman = cls.env.ref("base.user_demo")
        cls.account = cls.env["account.account"].search([], limit=1)
        cls.invoice = cls.env["account.invoice"].create(
            {
                "account_id": cls.account.id,
                "partner_id": cls.partner.id,
                "user_id": cls.salesman.id,
                "type": "out_invoice",
            }
        )

    def test_salesman_not_following(self):
        assert self.salesman.partner_id not in self.invoice.message_partner_ids
