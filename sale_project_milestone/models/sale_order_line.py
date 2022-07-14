# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
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
            "name": self.name,
            "estimated_hours": self._convert_qty_company_hours(),
        }

    def _create_milestone(self, vals):
        return self.env["project.milestone"].create(vals)

    def _setup_new_project(self):
        project = self._find_project_matching_template()

        if project:
            self.project_id = project
        else:
            self._timesheet_create_project()

    def _find_project_matching_template(self):
        for line in self.order_id.order_line:
            if (
                line.project_id
                and line.product_id.project_template_id
                == self.product_id.project_template_id
            ):
                return line.project_id

    #    @api.multi
    #    def write(self, vals):
    #        res = super().write(vals)
    #
    #        if "product_uom_qty" in vals:
    #            self._update_estimated_hours()
    #
    #        return res
    #
    #    @api.multi
    #    def _update_estimated_hours(self):
    #        for sol in self.filtered("milestone_id"):
    #            sol.milestone_id.estimated_hours = sol._convert_qty_company_hours()
    #
    #    @api.multi
    #    def _values_create_milestone(self, product, project):
    #        return {
    #            "name": "%s" % product.name,
    #            "project_id": project.id,
    #            "sale_line_id": self.id,
    #            "estimated_hours": self._convert_qty_company_hours(),
    #        }
    #
    #    @api.multi
    #    def _create_milestone_tasks(self, template_tasks, project, milestone):
    #        defaults = self._values_create_milestone_tasks(project, milestone)
    #        parents = {}
    #        child_tasks = {}
    #
    #        for task in template_tasks:
    #            parents, child_tasks = self._create_milestone_parent_tasks(
    #                defaults, task, parents, child_tasks
    #            )
    #
    #        for task, parent_task in child_tasks.items():
    #            defaults.update({"name": task.name, "parent_id": parents[parent_task]})
    #            task.copy(defaults)
    #
    #    @api.multi
    #    def _values_create_milestone_tasks(self, project, milestone):
    #        sale_line_name_parts = self.name.split("\n")
    #        partner = self.order_id.partner_id
    #        return {
    #            "project_id": project.id,
    #            "sale_line_id": self.id,
    #            "partner_id": partner.id,
    #            "email_from": partner.email,
    #            "milestone_id": milestone.id,
    #            "user_id": False,
    #            "email_cc": False,
    #            "company_id": self.company_id.id,
    #            "description": "<br/>".join(sale_line_name_parts[1:]),
    #        }
    #
    #    @api.multi
    #    def _create_milestone_parent_tasks(self, defaults, task, parents, child_tasks):
    #        parent = task.parent_id
    #
    #        if not parent:
    #            defaults["name"] = task.name
    #            parents[task] = task.copy(defaults).id
    #
    #        else:
    #            child_tasks[task] = parent
    #
    #        return parents, child_tasks
