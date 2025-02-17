# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    project_description = fields.Text("Project Description")

    def write(self, values):
        result = super().write(values)
        # changing the project_description should change the name of the linked project name
        if 'project_description' in values:
            for so in self:
                for project in so.order_line.mapped('project_id'):
                    name = project.name.split(
                        '|')[0] if '|' in project.name else project.name
                    project.name = " | ".join(
                        [name, so.project_description])
        return result
