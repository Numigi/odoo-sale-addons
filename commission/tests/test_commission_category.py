# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import operator
from functools import reduce
from .common import TestCommissionCase


class TestCommissionCategory(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_get_one_child(self):
        child_category = self._create_category("Child")
        self.category.child_ids = child_category
        assert self.category._get_all_children() == child_category

    def test_get_many_children(self):
        first_child = self._create_category("Child")
        second_child = self._create_category("Child's Child")
        self.category.child_ids = first_child
        first_child.child_ids = second_child
        assert self.category._get_all_children() == self._concatenate_categories(first_child, second_child)

    def test_get_no_children(self):
        assert not self.category._get_all_children()

    def test_sorted_by_dependencies(self):
        first_child = self._create_category("Child")
        second_child = self._create_category("Child's Child")
        self.category.child_ids = first_child
        first_child.child_ids = second_child

        categories = self._concatenate_categories(self.category, second_child, first_child)

        sorted_categories = categories._sorted_by_dependencies()
        assert sorted_categories == self._concatenate_categories(second_child, first_child, self.category)

    def _concatenate_categories(self, *categories):
        return reduce(operator.or_, categories)
