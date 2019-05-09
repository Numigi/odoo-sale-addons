# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from ddt import data, ddt
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


@ddt
class TestMinimumMarginConstrains(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_manager = cls.env['res.users'].create({
            'name': 'Stock Manager',
            'login': 'test_stock',
            'email': 'test_stock@test.com',
            'groups_id': [(4, cls.env.ref('stock.group_stock_manager').id)]
        })
        cls.sales_manager = cls.env['res.users'].create({
            'name': 'Sales Manager',
            'login': 'test_sales_manager',
            'email': 'test_sales_manager@test.com',
            'groups_id': [(4, cls.env.ref('sales_team.group_sale_manager').id)]
        })

        cls.category = cls.env['product.category'].create({
            'name': 'Category A',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'categ_id': cls.category.id,
            'price_type': 'dynamic',
        })

    def test_on_change__if_margin_lower_than_minimum__raise_error(self):
        self.category.minimum_margin = 0.30

        with self.env.do_in_onchange():
            self.product.margin = 0.29
            result = self.product._check_margin_is_not_lower_than_minimum_margin()
            assert isinstance(result, dict)
            assert result.get('warning')

    @data(0.30, 0.31)
    def test_on_change__if_not_lower_than_minimum__error_not_raised(self, margin):
        self.category.minimum_margin = 0.30

        with self.env.do_in_onchange():
            self.product.margin = margin
            result = self.product._check_margin_is_not_lower_than_minimum_margin()
            assert not result

    def test_on_write__if_margin_lower_and_not_sale_manager__raise_error(self):
        self.category.minimum_margin = 0.30

        with pytest.raises(ValidationError):
            self.product.sudo(self.stock_manager).write({'margin': 0.29})

    def test_on_write__if_margin_lower_and_sale_manager__error_not_raised(self):
        self.category.minimum_margin = 0.30

        self.product.sudo(self.sales_manager).write({'margin': 0.29})
        assert self.product.margin == 0.29

    @data(0.30, 0.31)
    def test_on_write__if_margin_not_lower_and_sale_manager__error_not_raised(self, margin):
        self.category.minimum_margin = 0.30

        self.product.sudo(self.sales_manager).write({'margin': margin})
        assert self.product.margin == margin

    def test_on_create__if_margin_lower_and_not_sale_manager__raise_error(self):
        self.category.minimum_margin = 0.30

        with pytest.raises(ValidationError):
            self.product.sudo(self.stock_manager).copy({'margin': 0.29})

    def test_on_create__if_margin_lower_and_sale_manager__error_not_raised(self):
        self.category.minimum_margin = 0.30

        new_product = self.product.sudo(self.sales_manager).copy({'margin': 0.29})
        assert new_product.margin == 0.29

    @data(0.30, 0.31)
    def test_on_create__if_margin_not_lower_and_not_sale_manager__error_not_raised(self, margin):
        self.category.minimum_margin = 0.30

        new_product = self.product.sudo(self.sales_manager).copy({'margin': margin})
        assert new_product.margin == margin


@ddt
class TestProductTemplateConstrains(TestMinimumMarginConstrains):
    """Do the same tests as above with product templates.

    The behavior on a product template is the same as on a variant.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.product.product_tmpl_id
