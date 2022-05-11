# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class ProjectTask(models.Model):

    _inherit = "project.task"

    @api.onchange("milestone_id")
    def onchange_milestone_id(self):
        milestone_sale_line = self.milestone_id.sale_line_id
        if milestone_sale_line:
            self.sale_line_id = milestone_sale_line

    @api.multi
    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if not "sale_line_id" in vals and "milestone_id" in vals and vals["milestone_id"]:
            self._update_milestone_sale_line_id()
        return res

    @api.multi
    def _update_milestone_sale_line_id(self):
        for task in self:
            milestone_sale_line = task.milestone_id.sale_line_id
            if milestone_sale_line:
                task.sale_line_id = milestone_sale_line
