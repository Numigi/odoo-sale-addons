# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytest
from odoo.exceptions import ValidationError
from .common import TestCommissionCase


class TestCommissionCategory(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_get_one_child(self):
        child_category = self._create_category("Child")
        self.category.child_category_ids = child_category
        assert self.category._get_all_children() == child_category

    def test_get_many_children(self):
        first_child = self._create_category("Child")
        second_child = self._create_category("Child's Child")
        self.category.child_category_ids = first_child
        first_child.child_category_ids = second_child

        children = self.category._get_all_children()

        assert children[0] == first_child
        assert children[1] == second_child

    def test_get_no_children(self):
        assert not self.category._get_all_children()

    def test_sorted_by_dependencies(self):
        first_child = self._create_category("Child")
        second_child = self._create_category("Child's Child")
        self.category.child_category_ids = first_child
        first_child.child_category_ids = second_child

        categories = self.category | second_child | first_child
        sorted_categories = categories._sorted_by_dependencies()

        assert sorted_categories[0] == second_child
        assert sorted_categories[1] == first_child
        assert sorted_categories[2] == self.category

    def test_no_self_child(self):
        with pytest.raises(ValidationError):
            self.category.child_category_ids = self.category

    def test_interval_date_invalid(self):
        category = self._create_category(name="Testing")
        with pytest.raises(ValidationError):
            self._create_category_rate(category, 50, 40)

    def test_category_onchange_no_rates(self):
        category = self._create_category(name="Testing")
        category.rate_type = "interval"
        target = self._create_target(target_amount=100000)
        target.category_id = category
        target.onchange_category_id()

        assert target.category_id == category
