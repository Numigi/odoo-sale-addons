# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestVariantSpecificPrice(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_template = cls.env['product.template'].create({'name': 'Product Template 1',})

        cls.attribute = cls.env['product.attribute'].create({'name': 'Attr', 'sequence': 1})
        cls.value_1 = cls.env['product.attribute.value'].create({
            'name': 'Value 1',
            'attribute_id': cls.attribute.id,
            'sequence': 1,
        })

        cls.value_2 = cls.env['product.attribute.value'].create({
            'name': 'Value 2',
            'attribute_id': cls.attribute.id,
            'sequence': 2,
        })
        cls.attribute_line = cls.env['product.template.attribute.line'].create({
            'product_tmpl_id': cls.product_template.id,
            'attribute_id': cls.attribute.id,
            'value_ids': [(6, 0, [cls.value_1.id, cls.value_2.id])],
        })
        cls.variant_1 = cls.product_template.product_variant_ids[0]
        cls.variant_2 = cls.product_template.product_variant_ids[1]

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
