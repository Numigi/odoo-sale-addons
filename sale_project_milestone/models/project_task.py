# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ProjectTask(models.Model):

    _inherit = "project.task"

    @api.onchange("milestone_id")
    def _onchange_milestone_id_set_sale_order_line(self):
        sale_line = self.milestone_id.sale_line_id
        if sale_line:
            self.sale_line_id = sale_line
