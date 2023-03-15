# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import SalePrivilegeLevelPricelistCase


class TestSalePrivilegeLevelPricelist(SalePrivilegeLevelPricelistCase):
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
        contact.invalidate_cache()
        contact.flush()
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

    def test_search(self):
        self.partner.country_id = self.canada
        pricelist_obj = self.env["product.pricelist"].with_context(
            sale_privilege_level_partner_id=self.partner.id
        )
        res = pricelist_obj.search([])
        assert res == self.pricelist_canada | self.pricelist_world
