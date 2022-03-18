# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_privilege_level_pricelist.tests.common import (
    SalePrivilegeLevelPricelistCase,
)


class TestSalePrivilegeLevelPricelist(SalePrivilegeLevelPricelistCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.level_a.write(
            {
                "name": "Level A",
                "rental_pricelist_ids": [
                    (0, 0, {"sequence": 1, "pricelist_id": cls.pricelist_france.id}),
                    (0, 0, {"sequence": 2, "pricelist_id": cls.pricelist_canada.id}),
                    (0, 0, {"sequence": 3, "pricelist_id": cls.pricelist_world.id}),
                ],
            }
        )

    def test_country_with_specific_pricelist(self):
        self.partner.country_id = self.canada
        assert self.partner.property_rental_pricelist == self.pricelist_canada

        self.partner.country_id = self.france
        assert self.partner.property_rental_pricelist == self.pricelist_france

    def test_country_with_no_specific_pricelist(self):
        self.partner.country_id = self.belgium
        assert self.partner.property_rental_pricelist == self.pricelist_world

    def test_no_country(self):
        self.partner.country_id = False
        assert self.partner.property_rental_pricelist == self.pricelist_world

    def test_pricelist_sequence(self):
        self.partner.country_id = self.france
        world_entry = self.level_a.rental_pricelist_ids.filtered(
            lambda l: l.pricelist_id == self.pricelist_world
        )
        world_entry.sequence = -1
        assert self.partner.property_rental_pricelist == self.pricelist_world
