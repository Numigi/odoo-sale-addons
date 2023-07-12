# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon
from odoo.tests import Form, tagged


@tagged('post_install', '-at_install')
class TestSaleCouponProgramRules(TestSaleCouponCommon):

    @classmethod
    def setUpClass(cls):
        super(TestSaleCouponProgramRules, cls).setUpClass()
        cls.Redmi10pro = cls.env['product.product'].create({'name': 'Redmi 10 Pro', 'list_price': 139.0})


        cls.p2 = cls.env['coupon.program'].create({
            'name': 'Buy Redmi10pro, get 10% discount',
            'promo_code_usage': 'no_code_needed',
            'reward_type': 'discount',
            'discount_type': 'percentage',
            'discount_percentage': 10,
            'program_type': 'promotion_program',
            'promo_applicability': 'on_current_order',
            'rule_products_domain': '["&",["list_price","=",139],["sale_ok","=",True]]',
            'discount_apply_on': 'all_products',

        })

    def test_shipping_cost_numbers(self):
        order = self.empty_order
        self.Redmi10pro.taxes_id = self.tax_10pc_incl
        sol1 = self.env['sale.order.line'].create({
            'product_id': self.Redmi10pro.id,
            'name': 'Redmi10pro',
            'product_uom_qty': 1,
            'order_id': order.id,
        })

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 2)
        self.assertEqual(order.reward_amount, -12.64)
        self.assertEqual(order.amount_untaxed, 113.72)



