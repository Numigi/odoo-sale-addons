# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.addons.sale_timesheet_service_generation_override.models import (
    sale_order_line as class_sale_order_line,
)

class_sale_order_line.SERVICE_TRACKING_EXISTING_PROJECT = [
    "task_global_project",
    "milestone_existing_project",
]
class_sale_order_line.SERVICE_TRACKING_NEW_PROJECT = [
    "project_only",
    "task_new_project",
    "milestone_new_project",
]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    milestone_id = fields.Many2one("project.milestone", string="Milestone", copy=False, index=True)

    @api.multi
    def _timesheet_service_generation(self):
        self = self.with_context(milestones_no_copy=True)
        return super(SaleOrderLine, self)._timesheet_service_generation()

    @api.multi
    def _create_service_tracking_existing_project(self, service_tracking, product):
        res = super(SaleOrderLine, self)._create_service_tracking_existing_project(
            service_tracking, product
        )

        if res and service_tracking == "milestone_existing_project":

            if not self.milestone_id:
                project = product.with_context(force_company=self.company_id.id).project_id
                project.use_milestones = True
                self._create_milestone(product, project)

            return False

        return res

    @api.multi
    def _create_milestone(self, product, project):
        milestone = self.env["project.milestone"].create(
            self._values_create_milestone(product, project)
        )
        project.use_milestones = True
        self.milestone_id = milestone
        milestone_template = product.milestone_template_id

        if milestone_template:
            self._create_milestone_tasks(
                milestone_template.with_context(active_test=False).project_task_ids,
                project,
                milestone,
            )

        else:
            milestone.project_id = project

        return milestone

    @api.multi
    def _values_create_milestone(self, product, project):
        return {
            "name": "%s" % product.name,
            "project_id": project.id,
            "sale_line_id": self.id,
            "estimated_hours": self._convert_qty_company_hours(),
        }

    @api.multi
    def _create_milestone_tasks(self, template_tasks, project, milestone):
        defaults = self._values_create_milestone_tasks(project, milestone)
        parents = {}
        child_tasks = {}

        for task in template_tasks:
            parents, child_tasks = self._create_milestone_parent_tasks(
                defaults, task, parents, child_tasks
            )

        for task, parent_task in child_tasks.items():
            defaults.update({"name": task.name, "parent_id": parents[parent_task]})
            task.copy(defaults)

    @api.multi
    def _values_create_milestone_tasks(self, project, milestone):
        sale_line_name_parts = self.name.split("\n")
        partner = self.order_id.partner_id
        return {
            "project_id": project.id,
            "sale_line_id": self.id,
            "partner_id": partner.id,
            "email_from": partner.email,
            "milestone_id": milestone.id,
            "user_id": False,
            "email_cc": False,
            "company_id": self.company_id.id,
            "description": "<br/>".join(sale_line_name_parts[1:]),
        }

    @api.multi
    def _create_milestone_parent_tasks(self, defaults, task, parents, child_tasks):
        parent = task.parent_id

        if not parent:
            defaults["name"] = task.name
            parents[task] = task.copy(defaults).id

        else:
            child_tasks[task] = parent

        return parents, child_tasks

    @api.multi
    def _create_service_tracking_new_project_option(self, project, service_tracking, product):
        res = super(SaleOrderLine, self)._create_service_tracking_new_project_option(
            project, service_tracking, product
        )

        if res and service_tracking == "milestone_new_project":
            self._milestone_project_creation(project, product)
            return False

        return res

    @api.multi
    def _milestone_project_creation(self, project, product):
        order = self.order_id
        project.name = order.name
        self._create_milestone(product, project)

        if product.project_template_id:
            project.with_context(active_test=False).tasks.filtered(
                lambda task: not task.active
            ).write(self._values_project_creation(order))

        return project

    @api.multi
    def _values_project_creation(self, order):
        partner = order.partner_id
        return {
            "sale_line_id": self.id,
            "partner_id": partner.id,
            "email_from": partner.email,
            "email_cc": False,
            "user_id": False,
        }

    @api.multi
    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)

        if "product_uom_qty" in vals:
            self._update_estimated_hours()

        return res

    @api.multi
    def _update_estimated_hours(self):
        for sol in self.filtered("milestone_id"):
            sol.milestone_id.estimated_hours = sol._convert_qty_company_hours()
