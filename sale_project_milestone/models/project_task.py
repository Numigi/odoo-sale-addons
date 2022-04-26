# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProjectTask(models.Model):

    _inherit = "project.task"

    milestone_sale_line_id = fields.Many2one(
        "sale.order.line",
        string="Sale order's product",
        related="milestone_id.sale_line_id",
        index=True,
        compute_sudo=True,
        store=True,
    )
