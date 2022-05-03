# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    milestone_id = fields.Many2one("project.milestone", string="Milestone", copy=False, index=True)

    @api.multi
    def _timesheet_service_generation(self):
        sol_null = self.env["sale.order.line"]

        for sol in self:
            self -= sol._case_milestone_service_tracking(sol_null)

        return super(SaleOrderLine, self)._timesheet_service_generation()

    @api.multi
    def _case_milestone_service_tracking(self, sol_null):
        sol_milestone = self.milestone_id

        if not sol_milestone:
            return self._milestone_service_tracking(sol_null)

        return sol_null

    @api.multi
    def _milestone_service_tracking(self, sol_null):
        product = self.product_id
        service_tracking = product.service_tracking

        if service_tracking == "milestone_existing_project":
            self._milestone_existing_project(product)
            return self

        elif service_tracking == "milestone_new_project":
            project_template = product.project_template_id
            sol_project = self._project_creation(project_template.id)
            self._create_milestone(product, sol_project, project_template)
            return self

        return sol_null

    @api.multi
    def _milestone_existing_project(self, product):
        project = product.with_context(force_company=self.company_id.id).project_id

        if project:
            self._create_milestone(product, project, False)

    @api.multi
    def _create_milestone(self, product, project, project_template):
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

        if project_template:
            project.with_context(active_test=False).tasks.write({"milestone_id": milestone.id})
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
    def _project_creation(self, project_template_id):
        order = self.order_id
        sol_project = self.with_context(milestones_no_copy=True)._timesheet_create_project()
        sol_project.name = order.name

        if project_template_id:
            sol_project.with_context(active_test=False).tasks.filtered(
                lambda task: not task.active
            ).write(self._values_project_creation(order))

        return sol_project

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
