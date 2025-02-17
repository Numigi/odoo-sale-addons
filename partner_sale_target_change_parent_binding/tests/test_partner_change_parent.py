# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestPartnerChangeParent(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_partner_change_parent_binding(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "company_type": "person",
            }
        )

        self.env["sale.target"].create(
            {
                "partner_id": partner.id,
                "date_start": "2023-01-01",
                "date_end": "2023-12-31",
                "sale_target": 500,
            }
        )

        wizard = (
            self.env["res.partner.change.parent"]
            .with_context(active_id=partner.id)
            .create(
                {
                    "contact_id": partner.id,
                }
            )
        )
        wizard.new_company_id = self.env.ref("base.res_partner_1").id
        # Check if _onchange_new_company_id is triggered and return a warning
        warning_message = wizard._onchange_new_company_id()
        self.assertEqual(
            warning_message["warning"]["title"],
            "Warning",
        )
