# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestComputeRental(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.rental_product_a = cls.env['product.product'].create({
            'name': 'Rental Service A',
            'type': 'service',
            'product_uom': cls.env.ref('product.product_uom_day').id,
        })

        cls.rental_product_b = cls.env['product.product'].create({
            'name': 'Rental Service B',
            'type': 'service',
            'product_uom': cls.env.ref('product.product_uom_day').id,
        })

        cls.product_a = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'rental_ok': True,
            'rental_product_id': cls.rental_product_a.id,
        })

        cls.product_b = cls.env['product.product'].create({
            'name': 'Product B',
            'type': 'product',
            'rental_ok': True,
            'rental_product_id': cls.rental_product_b.id,
        })

        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.env.ref('base.res_partner_1').id,
        })
