# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class SalePrivilegeLevelPricelistCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context={"testing_sale_privilege_level_pricelist": True})

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
