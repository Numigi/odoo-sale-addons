# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import SavepointCase


@tagged("post_install", "-at_install")
class TestSaleOrderPartnerRestrict(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.main_company = cls.env.ref("base.main_company")
        cls.partner_model = cls.env["res.partner"]

        cls.partner_parent = cls.partner_model.create(
            {"name": "Partner Parent", "type": "contact"}
        )
        cls.partner_affiliate = cls.partner_model.create(
            {
                "name": "Affiliate partner",
                "company_type": "company",
                "parent_id": cls.partner_parent.id,
            }
        )
        cls.affiliate_child = cls.partner_model.create(
            {
                "name": "Affiliate Child",
                "company_type": "person",
                "parent_id": cls.partner_affiliate.id,
            }
        )

    def _create_sale_order(self, partner):
        so = self.env["sale.order"].create(
            {"partner_id": partner.id, "name": "/", "company_id": self.main_company.id}
        )
        return so

    def test_sale_order_partner_restrict_option_only_children(self):
        """Test for a restriction with the "Only children" option"""
        self.main_company.sale_order_partner_restrict = "affiliate_contact"

        self.assertTrue(
            self._create_sale_order(self.partner_affiliate),
            "Affilaites partner "
            "should be available in 'affiliate_contact' option",
        )

        self.assertTrue(
            self._create_sale_order(self.affiliate_child),
            "Affilaite Child partner "
            "should be available in 'affiliate_contact' option",
        )

        # parent partner shouldn't be available in 'affiliate_contact' option
        with self.assertRaises(ValidationError):
            self._create_sale_order(self.partner_parent)

