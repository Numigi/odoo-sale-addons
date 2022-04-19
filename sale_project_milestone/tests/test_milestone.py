# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import MilestoneCase


class TestMilestone(MilestoneCase):
    def test_product_new_milestone_existing_project_elements(self):
        product = self.product_new_milestone_existing_project
        test1, test2, test3 = self.nb_elements_tests(
            product, nb_milestones=1, nb_tasks=0, nb_projects=1
        )
        assert test1
        assert test2
        assert test3

    def test_product_new_milestone_existing_project_values(self):
        product = self.product_new_milestone_existing_project
        test1, test2, test3 = self.values_common(product)
        assert test1
        assert test2
        assert test3

    def test_product_new_milestone_new_project_elements(self):
        product = self.product_new_milestone_new_project
        test1, test2, test3 = self.nb_elements_tests(
            product, nb_milestones=1, nb_tasks=0, nb_projects=1
        )
        assert test1
        assert test2
        assert test3

    def test_product_new_milestone_new_project_values(self):
        product = self.product_new_milestone_new_project
        test1, test2, test3, test4, test5, test6 = self.values_create_project(product)
        assert test1
        assert test2
        assert test3
        assert test4
        assert test5
        assert test6

    def test_product_new_milestone_template_project_elements(self):
        product = self.product_new_milestone_template_project
        test1, test2, test3 = self.nb_elements_tests(
            product, nb_milestones=1, nb_tasks=3, nb_projects=1
        )
        assert test1
        assert test2
        assert test3

    def test_product_new_milestone_template_project_values(self):
        product = self.product_new_milestone_template_project
        test1, test2, test3, test4, test5, test6, test7, test8 = self.values_create_project(
            product, create_tasks=1
        )
        assert test1
        assert test2
        assert test3
        assert test4
        assert test5
        assert test6
        assert test7
        assert test8

    def test_product_milestone_template_new_project_elements(self):
        product = self.product_milestone_template_new_project
        test1, test2, test3 = self.nb_elements_tests(
            product, nb_milestones=1, nb_tasks=3, nb_projects=1
        )
        assert test1
        assert test2
        assert test3

    def test_product_milestone_template_new_project_values(self):
        product = self.product_milestone_template_new_project
        test1, test2, test3, test4, test5, test6, test7, test8 = self.values_create_project(
            product, create_tasks=1
        )
        assert test1
        assert test2
        assert test3
        assert test4
        assert test5
        assert test6
        assert test7
        assert test8

    def test_change_qty_line__change_qty_milestone_estimated_hours(self):
        product = self.product_new_milestone_existing_project
        sale = self.sale_order_confirm_to_cancel_to_draft(product)
        sol = sale.order_line
        milestone = sol.milestone_id
        milestone_qty = milestone.estimated_hours
        sol.product_uom_qty = 10.0
        new_milestone_qty = milestone.estimated_hours
        assert new_milestone_qty == sol._convert_qty_company_hours() != milestone_qty
