# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.canada = cls.env.ref("base.ca")
        cls.france = cls.env.ref("base.fr")
        cls.country_group_canada = cls.env["res.country.group"].create(
            {"name": "Canada", "country_ids": [(4, cls.canada.id)]}
        )
        cls.country_group_europe = cls.env["res.country.group"].create(
            {"name": "Europe", "country_ids": [(4, cls.france.id)]}
        )

        cls.pricelist_canada = cls.env["product.pricelist"].create(
            {
                "name": "Pricelist Canada",
                "country_group_id": cls.country_group_canada.id,
            }
        )
        cls.pricelist_europe = cls.env["product.pricelist"].create(
            {
                "name": "Pricelist Europe",
                "country_group_id": cls.country_group_europe.id,
            }
        )

        cls.level_a = cls.env["sale.privilege.level"].create(
            {
                "name": "Level A",
                "pricelist_ids": [
                    (4, cls.pricelist_canada.id),
                    (4, cls.pricelist_europe.id),
                ],
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner A",
                "is_company": True,
                "privilege_level_id": cls.level_a.id,
            }
        )

    def test_compute_partner_pricelist(self):
        self.partner.country_id = self.canada
        assert self.partner.property_product_pricelist == self.pricelist_canada

        self.partner.country_id = self.france
        assert self.partner.property_product_pricelist == self.pricelist_europe
