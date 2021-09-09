# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestVariantSpecificPrice(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.variant_1 = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
        })
        cls.variant_2 = cls.variant_1.copy({'product_tmpl_id': cls.variant_1.product_tmpl_id.id})
        cls.variant_1_price = 100
        cls.variant_2_price = 200
        cls.variant_1.list_price = cls.variant_1_price
        cls.variant_2.list_price = cls.variant_2_price
        cls.variant_1.refresh()
        cls.variant_2.refresh()

    def test_each_variant_has_distinct_lst_price(self):
        assert self.variant_1.lst_price == self.variant_1_price
        assert self.variant_2.lst_price == self.variant_2_price

    def test_each_variant_has_distinct_list_price(self):
        assert self.variant_1.list_price == self.variant_1_price
        assert self.variant_2.list_price == self.variant_2_price
