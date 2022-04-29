# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class MilestoneCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env["ir.config_parameter"].sudo().set_param("project.group_subtask_project", True)

        cls.project_billable_type_no = cls.env["project.project"].create(
            {"name": "Project billable type no"}
        )
        cls.project_template_type_no = cls.env["project.project"].create(
            {"name": "Project template billable type no"}
        )

        cls.milestone_template = cls.env["project.milestone"].create(
            {"name": "Milestone template", "project_id": cls.project_template_type_no.id}
        )

        cls.task_1 = cls.env["project.task"].create(
            {
                "name": "My Task 1",
                "project_id": cls.project_billable_type_no.id,
            }
        )

        cls.task_2 = cls.env["project.task"].create(
            {
                "name": "My Subtask 2",
                "project_id": cls.project_billable_type_no.id,
                "parent_id": cls.task_1.id,
            }
        )

        cls.task_3 = cls.env["project.task"].create(
            {
                "name": "My Task 3",
                "project_id": cls.project_billable_type_no.id,
                "active": False,
            }
        )

        cls.task_template_1 = cls.env["project.task"].create(
            {
                "name": "My Template Task 1",
                "project_id": cls.project_template_type_no.id,
                "milestone_id": cls.milestone_template.id,
            }
        )

        cls.task_template_2 = cls.env["project.task"].create(
            {
                "name": "My Template Subtask 2",
                "project_id": cls.project_template_type_no.id,
                "milestone_id": cls.milestone_template.id,
                "parent_id": cls.task_template_1.id,
            }
        )

        cls.task_template_3 = cls.env["project.task"].create(
            {
                "name": "My Template Task 3",
                "project_id": cls.project_template_type_no.id,
                "milestone_id": cls.milestone_template.id,
                "active": False,
            }
        )

        cls.product_consumable = cls.env["product.product"].create({"name": "Consumable"})
        cls.product_new_milestone_existing_project = cls.env["product.product"].create(
            {
                "name": "New milestone existing project",
                "type": "service",
                "service_tracking": "milestone_existing_project",
                "project_id": cls.project_billable_type_no.id,
            }
        )
        cls.product_new_milestone_new_project = cls.env["product.product"].create(
            {
                "name": "New milestone new project",
                "type": "service",
                "service_tracking": "milestone_new_project",
            }
        )
        cls.product_new_milestone_template_project = cls.env["product.product"].create(
            {
                "name": "New milestone template project",
                "type": "service",
                "service_tracking": "milestone_new_project",
                "project_template_id": cls.project_billable_type_no.id,
            }
        )
        cls.product_milestone_template_new_project = cls.env["product.product"].create(
            {
                "name": "Milestone template new project",
                "type": "service",
                "service_tracking": "milestone_new_project",
                "milestone_template_id": cls.milestone_template.id,
            }
        )

        cls.customer = cls.env.ref("base.res_partner_1")

    @classmethod
    def generate_sale_order_confirmed(cls, product):
        sale = cls.env["sale.order"].create({"partner_id": cls.customer.id})
        sale_line = cls.env["sale.order.line"].create(
            {
                "product_id": product.id,
                "order_id": sale.id,
                "name": product.name,
                "product_uom_qty": 2,
                "product_uom": product.uom_id.id,
                "price_unit": product.list_price,
                "tax_id": False,
            }
        )
        sale_line.product_id_change()
        sale.action_confirm()
        return sale

    @classmethod
    def nb_elements_tests(cls, product, nb_milestones, nb_tasks, nb_projects):
        sale = cls.generate_sale_order_confirmed(product)
        milestones = sale.milestone_ids
        test1 = len(milestones) == nb_milestones
        test2 = len(milestones.with_context(active_test=False).project_task_ids) == nb_tasks
        test3 = len(milestones.project_id) == nb_projects
        return test1, test2, test3

    @classmethod
    def values_common(cls, product, create_project=0):
        sale = cls.generate_sale_order_confirmed(product)
        milestones = sale.milestone_ids
        order_line = sale.order_line
        test1 = milestones.name == product.name
        test2 = milestones.sale_line_id == order_line
        test3 = milestones.estimated_hours == order_line.product_uom_qty
        if create_project:
            return sale, test1, test2, test3
        else:
            return test1, test2, test3

    @classmethod
    def values_create_project(cls, product, create_tasks=0):
        sale, test1, test2, test3 = cls.values_common(product, 1)
        milestones = sale.milestone_ids
        project = milestones.project_id
        order_line = sale.order_line
        test4 = project.name == sale.name
        test5 = project.sale_order_id == sale
        test6 = project.sale_line_id == order_line
        if create_tasks:
            tasks = milestones.with_context(active_test=False).project_task_ids
            test7 = len(tasks.filtered(lambda task: task.sale_line_id & order_line)) == 3
            test8 = tasks.filtered(lambda task: task.parent_id).parent_id & tasks
            return test1, test2, test3, test4, test5, test6, test7, test8
        else:
            return test1, test2, test3, test4, test5, test6

    @classmethod
    def sale_order_confirm_to_cancel_to_draft(cls, product):
        sale = cls.generate_sale_order_confirmed(product)
        sale.action_cancel()
        sale.action_draft()
        return sale
