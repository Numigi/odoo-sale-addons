# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ProjectProject(models.Model):

    _inherit = "project.project"

    def copy(self, default=None):
        if default is None:
            default = {}

        if self._context.get("project_no_copy_tasks"):
            default["tasks"] = []

        return super().copy(default)
