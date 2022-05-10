# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api
from odoo.addons.sale_timesheet.models.sale_order import SaleOrderLine as class_sale_order_line

SERVICE_TRACKING_EXISTING_PROJECT = ["task_global_project"]
SERVICE_TRACKING_NEW_PROJECT = ["project_only", "task_new_project"]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _timesheet_service_generation_override(self):
        map_projects = self._initialize_map_projects()
        do_maps_projects = True
        orders = self.mapped("order_id")

        for sol in self:

            if sol.is_service:
                product = sol.product_id
                service_tracking = product.service_tracking

                if service_tracking:
                    (
                        map_projects,
                        do_maps_projects,
                    ) = sol._create_service_tracking(
                        map_projects,
                        do_maps_projects,
                        product,
                        service_tracking,
                        orders,
                    )

    @api.multi
    def _initialize_map_projects(self):
        return {"map_so_project": {}, "map_so_project_templates": {}}

    @api.multi
    def _create_service_tracking(
        self, map_projects, do_maps_projects, product, service_tracking, orders
    ):

        if service_tracking in SERVICE_TRACKING_EXISTING_PROJECT:
            self._create_service_tracking_existing_project(service_tracking, product)

            return map_projects, do_maps_projects

        if service_tracking in SERVICE_TRACKING_NEW_PROJECT:

            if do_maps_projects:
                map_projects = self._do_maps_projects(map_projects, orders)
                do_maps_projects = False

            map_projects = self._create_service_tracking_new_project(map_projects, product, service_tracking)

        return map_projects, do_maps_projects

    @api.multi
    def _create_service_tracking_existing_project(self, service_tracking, product):

        if service_tracking == "task_global_project":

            if not self.task_id:
                project = product.with_context(force_company=self.company_id.id).project_id
                self._timesheet_create_task(project=project)

    @api.multi
    def _do_maps_projects(self, map_projects, orders):
        sol = self.search(
            [
                ("order_id", "in", orders.ids),
                ("project_id", "!=", False),
                ("product_id.service_tracking", "in", SERVICE_TRACKING_NEW_PROJECT),
            ]
        )
        sol_with_project = sol.filtered(
            lambda sol: not sol.product_id.project_template_id
        )
        map_projects["map_so_project"] = {
            sol.order_id.id: sol.project_id for sol in sol_with_project
        }
        sol_with_project_templates = sol - sol_with_project
        map_projects["map_so_project_templates"] = {
            (sol.order_id.id, sol.product_id.project_template_id.id): sol.project_id
            for sol in sol_with_project_templates
        }
        return map_projects

    @api.multi
    def _create_service_tracking_new_project(self, map_projects, product, service_tracking):

        if self.project_id:
            return map_projects

        project_template_id = product.project_template_id.id
        order_id = self.order_id.id

        if self._can_create_project_override(map_projects, project_template_id, order_id):
            project = self._timesheet_create_project()

            if project_template_id:
                map_projects["map_so_project_templates"][(order_id, project_template_id)] = project

            else:
                map_projects["map_so_project"][order_id] = project

        else:
            project = map_projects["map_so_project_templates"].get(
                (order_id, project_template_id)
            ) or map_projects["map_so_project"].get(order_id)
            self.project_id = project
        self._create_service_tracking_new_project_option(project, service_tracking)

        return map_projects

    @api.multi
    def _can_create_project_override(self, map_projects, project_template_id, order_id):

        if project_template_id:
            return (order_id, project_template_id) not in map_projects["map_so_project_templates"]

        elif order_id not in map_projects["map_so_project"]:
            return True

        return False

    @api.multi
    def _create_service_tracking_new_project_option(self, project, service_tracking):

        if service_tracking == "task_new_project":

            if not self.task_id:
                self._timesheet_create_task(project=project)


class_sale_order_line._timesheet_service_generation = (
    SaleOrderLine._timesheet_service_generation_override
)
