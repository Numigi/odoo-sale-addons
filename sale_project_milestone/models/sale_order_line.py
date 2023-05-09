# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    milestone_id = fields.Many2one(
        "project.milestone",
        string="Milestone",
        copy=False,
        index=True,
    )

    def write(self, vals):
        res = super().write(vals)

        if "product_uom_qty" in vals:
            self._update_milestone_estimated_hours()

        return res

    def _update_milestone_estimated_hours(self):
        for line in self.filtered("milestone_id"):
            line.milestone_id.estimated_hours = line._convert_qty_company_hours(
                self.task_id.company_id)

    def _timesheet_service_generation(self):
        lines_existing_project = self.filtered(
            lambda l: l.is_service
            and l.product_id.service_tracking == "milestone_existing_project"
        )
        lines_new_project = self.filtered(
            lambda l: l.is_service
            and l.product_id.service_tracking == "milestone_new_project"
        )
        other_lines = self - lines_existing_project - lines_new_project

        super(SaleOrderLine, other_lines)._timesheet_service_generation()

        for line in lines_existing_project:
            line._generate_milestone_existing_project()

        for line in lines_new_project:
            line._generate_milestone_new_project()

    def _generate_milestone_existing_project(self):
        vals = self._get_milestone_existing_project_vals()
        self.milestone_id = self._create_milestone(vals)

    def _generate_milestone_new_project(self):
        vals = self._get_milestone_new_project_vals()
        self.milestone_id = self._create_milestone(vals)

        template = self.product_id.milestone_template_id
        if template:
            self._copy_tasks_from_milestone_template(template)

        self.project_id.use_milestones = True

    def _get_milestone_existing_project_vals(self):
        vals = self._get_milestone_common_vals()
        vals["project_id"] = self.product_id.project_id.id
        return vals

    def _get_milestone_new_project_vals(self):
        self._setup_new_project()
        vals = self._get_milestone_common_vals()
        vals["project_id"] = self.project_id.id
        return vals

    def _get_milestone_common_vals(self):
        return {
            "name": self.product_id.display_name,
            "estimated_hours": self._convert_qty_company_hours(self.task_id.company_id),
            "sale_line_id": self.id,
        }

    def _create_milestone(self, vals):
        return self.env["project.milestone"].create(vals)

    def _copy_tasks_from_milestone_template(self, template):
        all_tasks = template.project_task_ids
        parent_tasks = all_tasks - all_tasks.mapped("child_ids")

        for task in parent_tasks:
            self._copy_milestone_task(task)

    def _copy_milestone_task(self, template_task):
        vals = self._get_milestone_task_vals(template_task)
        task = template_task.copy(vals)

        for template_subtask in template_task.child_ids:
            vals = self._get_milestone_task_vals(template_subtask)
            vals["parent_id"] = task.id
            subtask = template_subtask.copy(vals)

        return task

    def _get_milestone_task_vals(self, task):
        return {
            "name": task.name,
            "partner_id": self.order_id.partner_id.id,
            "email_from": self.order_id.partner_id.email,
            "project_id": self.milestone_id.project_id.id,
            "milestone_id": self.milestone_id.id,
            "sale_line_id": self.id,
            "company_id": self.company_id.id,
            "user_id": False,
        }

    def _setup_new_project(self):
        project = self._find_project_matching_template()

        if project:
            self.project_id = project
        else:
            self.with_context(
                project_no_copy_tasks=True)._timesheet_create_project()

    def _find_project_matching_template(self):
        for line in self.order_id.order_line:
            if (
                line.project_id
                and line.product_id.project_template_id
                == self.product_id.project_template_id
            ):
                return line.project_id
