# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import data, ddt, unpack
from odoo.tests.common import SavepointCase
from odoo.tools.float_utils import float_round


@ddt
class TestSaleOrderInForeignCurrency(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.usd = cls.env.user.company_id.currency_id
        cls.cad = cls.env.ref('base.CAD')

        # Remove any existing currency rate
        cls.env['res.currency.rate'].search([]).unlink()

        cls.currency_rate = cls.env['res.currency.rate'].create({
            'currency_id': cls.cad.id,
            'rate': 1.5,
        })

        cls.product = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'price_type': 'dynamic',
            'minimum_margin': 0,
            'margin': 0.30,
            'price_rounding': '1',
            'price_surcharge': 0,
            'standard_price': 70,
        })

        cls.customer = cls.env['res.partner'].create({
            'name': 'My Customer',
            'customer': True,
        })

        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'CAD Pricelist',
            'currency_id': cls.cad.id,
            'item_ids': [(0, 0, {
                'applied_on': '3_global',
                'base': 'list_price',
                'compute_price': 'formula',
            })],
        })

        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'pricelist_id': cls.pricelist.id,
            'order_line': [
                (0, 0, {
                    'product_id': cls.product.id,
                    'name': cls.product.name,
                    'product_uom': cls.env.ref('uom.product_uom_unit').id,
                    'product_uom_qty': 1,
                })
            ]
        })
        cls.line = cls.sale_order.order_line

    def test_currency_rate_applied_to_product_price(self):
        self.product.update_sale_price_from_cost()
        self.line.product_uom_change()
        self.line.refresh()
        assert self.line.price_unit == 150  # (70 / (1 - 0.30)) * 1.5

    @data(
        ('0.01', 123.46),
        ('0.05', 123.45),
        ('0.1', 123.50),
        ('1', 123.00),
        ('10', 120.00),
    )
    @unpack
    def test_price_rounding_applied_to_sale_order_line(self, rounding, expected_price):
        self.product.price_rounding = rounding
        self.product.update_sale_price_from_cost()
        self.currency_rate.rate = 1.23456
        self.line.product_uom_change()
        self.line.refresh()
        assert self.line.price_unit == expected_price  # (70 / (1 - 0.30)) * currency_rate

    @data(
        (0, 150.00),
        (False, 150.00),
        (-0.01, 149.99),
        (-0.03, 149.97),
    )
    @unpack
    def test_price_surcharge_applied_to_sale_order_line(self, surcharge, expected_price):
        self.product.price_surcharge = surcharge
        self.product.update_sale_price_from_cost()
        self.line.product_uom_change()
        self.line.refresh()
        assert self.line.price_unit == expected_price  # (70 / (1 - 0.30)) * currency_rate
