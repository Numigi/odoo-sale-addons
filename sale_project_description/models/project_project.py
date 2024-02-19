# © 2024 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class ProjectProject(models.Model):

    _inherit = "project.project"

    def create(self, vals):
        res = super().create(vals)
        if "sale_order_id" in vals and res.sale_order_id.project_description:
            res["name"] = " | ".join(
                [res["name"], res.sale_order_id.project_description])
        return res
