# © 2024 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api


class ProjectProject(models.Model):

    _inherit = "project.project"

    @api.model
    def create(self, vals):
        # Prevent double project creation
        self = self.with_context(mail_create_nosubscribe=True)
        project = super(ProjectProject, self).create(vals)
        if (
            "sale_order_id" in vals
            and vals.get("sale_order_id")
            and project.sale_order_id.project_description
        ):
            project["name"] = " | ".join(
                [project["name"], project.sale_order_id.project_description])
        return project
