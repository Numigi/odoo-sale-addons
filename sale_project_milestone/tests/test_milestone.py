# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestMilestone(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create(
            {
                "name": "My Project",
            }
        )
        cls.project_template = cls.env["project.project"].create(
            {
                "name": "My Template Project",
            }
        )
        cls.project_template_2 = cls.project_template.copy()
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")

        cls.milestone_template = cls.env["project.milestone"].create(
            {
                "name": "My Milestone",
                "project_id": cls.project.id,
            }
        )

        cls.task = cls.env["project.task"].create(
            {
                "name": "My Task",
                "project_id": cls.project.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "My Product",
                "type": "service",
            }
        )
        cls.product_2 = cls.product.copy()

        cls.customer = cls.env.ref("base.res_partner_1")

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
            }
        )
        cls.number_of_hours = 2
        cls.order_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product.id,
                "name": cls.product.name,
                "product_uom_qty": cls.number_of_hours,
                "product_uom": cls.uom_hour.id,
                "price_unit": 10,
            }
        )

    def test_milestone_existing_project(self):
        self.product.write(
            {
                "service_tracking": "milestone_existing_project",
                "project_id": self.project.id,
            }
        )
        self.order.action_confirm()
        assert not self.order_line.task_id
        assert not self.order_line.project_id

        milestone = self.order_line.milestone_id
        assert milestone
        assert milestone.project_id == self.project
        assert milestone.estimated_hours == self.number_of_hours

    def test_milestone_in_new_project(self):
        self.product.write(
            {
                "service_tracking": "milestone_new_project",
                "project_template_id": self.project_template.id,
            }
        )
        self.order.action_confirm()
        assert not self.order_line.task_id

        milestone = self.order_line.milestone_id
        assert milestone
        assert milestone.estimated_hours == self.number_of_hours

        project = self.order_line.project_id
        assert project
        assert project == milestone.project_id
        assert project != self.project_template
        assert self.project_template.name in project.name

    def test_two_milestones_in_same_project(self):
        self.product.write(
            {
                "service_tracking": "milestone_new_project",
                "project_template_id": self.project_template.id,
            }
        )
        line_1 = self.order_line
        line_2 = self.order_line.copy({"order_id": self.order.id})
        self.order.action_confirm()

        assert line_1.milestone_id
        assert line_2.milestone_id
        assert line_1.milestone_id != line_2.milestone_id

        assert line_1.project_id
        assert line_2.project_id
        assert line_1.project_id == line_2.project_id

    def test_two_milestones_in_distinct_projects(self):
        self.product.write(
            {
                "service_tracking": "milestone_new_project",
                "project_template_id": self.project_template.id,
            }
        )
        self.product_2.write(
            {
                "service_tracking": "milestone_new_project",
                "project_template_id": self.project_template_2.id,
            }
        )
        line_1 = self.order_line
        line_2 = self.order_line.copy(
            {
                "order_id": self.order.id,
                "product_id": self.product_2.id,
            }
        )
        self.order.action_confirm()

        assert line_1.milestone_id
        assert line_2.milestone_id
        assert line_1.milestone_id != line_2.milestone_id

        assert line_1.project_id
        assert line_2.project_id
        assert line_1.project_id != line_2.project_id

    def test_milestone_and_task_in_same_projects(self):
        self.product.write(
            {
                "service_tracking": "task_new_project",
                "project_template_id": self.project_template.id,
            }
        )
        self.product_2.write(
            {
                "service_tracking": "milestone_new_project",
                "project_template_id": self.project_template.id,
            }
        )
        line_1 = self.order_line
        line_2 = self.order_line.copy(
            {
                "order_id": self.order.id,
                "product_id": self.product_2.id,
            }
        )
        self.order.action_confirm()

        assert line_1.task_id
        assert not line_1.milestone_id
        assert not line_2.task_id
        assert line_2.milestone_id

        assert line_1.project_id
        assert line_2.project_id
        assert line_1.project_id == line_2.project_id

    def test_milestone_in_main_project(self):
        self.product.write(
            {
                "service_tracking": "milestone_new_project",
            }
        )
        self.order.action_confirm()

        assert self.order_line.milestone_id
        assert self.order_line.project_id

    def test_milestone_and_task_in_main_project(self):
        self.product.write(
            {
                "service_tracking": "task_new_project",
            }
        )
        self.product_2.write(
            {
                "service_tracking": "milestone_new_project",
            }
        )
        line_1 = self.order_line
        line_2 = self.order_line.copy(
            {
                "order_id": self.order.id,
                "product_id": self.product_2.id,
            }
        )
        self.order.action_confirm()

        assert line_1.task_id
        assert not line_1.milestone_id
        assert not line_2.task_id
        assert line_2.milestone_id

        assert line_1.project_id
        assert line_2.project_id
        assert line_1.project_id == line_2.project_id

