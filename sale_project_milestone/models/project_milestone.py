# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json

from odoo import fields, models, api


class ProjectMilestone(models.Model):

    _inherit = "project.milestone"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.user.company_id,
    )
    sale_line_id = fields.Many2one("sale.order.line", string="Sale line", copy=False, index=True)
    order_id = fields.Many2one(
        "sale.order",
        related="sale_line_id.order_id",
        string="Sale order",
        index=True,
        compute_sudo=True,
        store=True,
    )
    domain_sale_line_id = fields.Char(
        compute="_compute_domain_sale_line_id",
        readonly=True,
        store=False,
    )

    @api.multi
    @api.depends(
        "project_id",
        "project_id.sale_order_id",
    )
    def _compute_domain_sale_line_id(self):
        for milestone in self:
            milestone.domain_sale_line_id = json.dumps(
                [
                    ("order_id", "=", self.project_id.sale_order_id.id),
                    ("product_id.type", "=", "service"),
                    ("product_id.service_tracking", "!=", "no"),
                ]
            )

    @api.onchange("project_id")
    def onchange_project_id(self):
        self.sale_line_id = False

    @api.onchange("sale_line_id", "project_id")
    def onchange_sale_line_id(self):
        self.estimated_hours = self.sale_line_id._convert_qty_company_hours()

    @api.multi
    def write(self, vals):
        res = super(ProjectMilestone, self).write(vals)
        if "sale_line_id" in vals and vals["sale_line_id"]:
            self._update_task_sale_line_id()
        return res

    @api.multi
    def _update_task_sale_line_id(self):
        for milestone in self:
            milestone.with_context(ative_test=False).project_task_ids.write(
                {"sale_line_id": milestone.sale_line_id.id}
            )
