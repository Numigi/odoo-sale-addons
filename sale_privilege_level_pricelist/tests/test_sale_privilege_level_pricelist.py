# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.canada = cls.env.ref("base.ca")
        cls.france = cls.env.ref("base.fr")
        cls.belgium = cls.env.ref("base.be")
        cls.pricelist_canada = cls._make_pricelist("Canada Prices", cls.canada)
        cls.pricelist_france = cls._make_pricelist("France Prices", cls.france)
        cls.pricelist_world = cls._make_pricelist("World Prices")

        cls.level_a = cls.env["sale.privilege.level"].create(
            {
                "name": "Level A",
                "pricelist_ids": [
                    (0, 0, {"sequence": 1, "pricelist_id": cls.pricelist_france.id}),
                    (0, 0, {"sequence": 2, "pricelist_id": cls.pricelist_canada.id}),
                    (0, 0, {"sequence": 3, "pricelist_id": cls.pricelist_world.id}),
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

    @classmethod
    def _make_pricelist(cls, name, countries=None):
        pricelist = cls.env["product.pricelist"].create({"name": name})
        if countries:
            pricelist.country_group_ids = cls._make_country_group(countries)
        return pricelist

    @classmethod
    def _make_country_group(cls, countries):
        country_group = cls.env["res.country.group"].create(
            {"name": ",".join(countries.mapped("name"))}
        )
        country_group.country_ids = countries
        return country_group

    def test_country_with_specific_pricelist(self):
        self.partner.country_id = self.canada
        assert self.partner.property_product_pricelist == self.pricelist_canada

        self.partner.country_id = self.france
        assert self.partner.property_product_pricelist == self.pricelist_france

    def test_country_with_no_specific_pricelist(self):
        self.partner.country_id = self.belgium
        assert self.partner.property_product_pricelist == self.pricelist_world

    def test_no_country(self):
        self.partner.country_id = False
        assert self.partner.property_product_pricelist == self.pricelist_world

    def test_pricelist_sequence(self):
        self.partner.country_id = self.france
        world_entry = self.level_a.pricelist_ids.filtered(
            lambda l: l.pricelist_id == self.pricelist_world
        )
        world_entry.sequence = -1
        assert self.partner.property_product_pricelist == self.pricelist_world

    def test_commercial_partner_privilege_level(self):
        contact = self.env["res.partner"].create(
            {
                "name": "Contact A",
                "parent_id": self.partner.id,
                "type": "invoice",
                "country_id": self.canada.id,
                "privilege_level_id": False,
            }
        )
        assert contact.property_product_pricelist == self.pricelist_canada

    def test_no_privilege_level(self):
        self.partner.privilege_level_id = False
        assert not self.partner.property_product_pricelist

    def test_external_user_can_compute_pricelist(self):
        portal_user = self.env["res.users"].create(
            {
                "name": "User A",
                "email": "usera@example.com",
                "login": "usera@example.com",
                "partner_id": self.partner.id,
                "groups_id": [(4, self.env.ref("base.group_portal").id)],
            }
        )
        partner = self.partner.sudo(portal_user)
        assert partner.property_product_pricelist
