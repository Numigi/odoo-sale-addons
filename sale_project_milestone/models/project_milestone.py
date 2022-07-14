# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProjectMilestone(models.Model):

    _inherit = "project.milestone"

    sale_line_id = fields.Many2one("sale.order.line", string="Sale line", copy=False, index=True)
    order_id = fields.Many2one(
        "sale.order",
        related="sale_line_id.order_id",
        string="Sale order",
        index=True,
        compute_sudo=True,
        store=True,
    )
