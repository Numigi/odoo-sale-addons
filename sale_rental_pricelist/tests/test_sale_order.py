# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rental_pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Rental",
                "rental": True,
            }
        )

        cls.partner = cls.env["res.partner"].create({"name": "My Customer"})
        cls.partner.property_rental_pricelist_id = cls.rental_pricelist

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

    def test_onchange_partner__set_sale_pricelist(self):
        self.order.is_rental = False
        self.order.onchange_partner_id()
        assert self.order.pricelist_id != self.rental_pricelist

    def test_onchange_partner__set_rental_pricelist(self):
        self.order.is_rental = True
        self.order.onchange_partner_id()
        assert self.order.pricelist_id == self.rental_pricelist
