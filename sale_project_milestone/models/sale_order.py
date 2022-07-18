# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class SaleOrder(models.Model):

    _inherit = "sale.order"

    milestone_ids = fields.One2many("project.milestone", "order_id", sting="Milestones")

    milestone_count = fields.Integer(
        compute="_get_milestone_count", string="Milestone Count", readonly=True
    )

    @api.multi
    @api.depends("milestone_ids")
    def _get_milestone_count(self):
        for order in self:
            order.milestone_count = len(order.milestone_ids)

    @api.multi
    def action_view_milestone(self):
        milestone_ids = self.milestone_ids.ids
        action = self.env.ref("project_milestone.project_milestone_action").read()[0]

        if len(milestone_ids) > 1:
            action["domain"] = [("id", "in", milestone_ids)]

        elif len(milestone_ids) == 1:
            action = self._get_action_view_milestone(action)
            action["res_id"] = milestone_ids[0]

        else:
            action = {"type": "ir.actions.act_window_close"}

        return action

    @api.multi
    def _get_action_view_milestone(self, action):
        form_view = [(self.env.ref("project_milestone.project_milestone_view_form").id, "form")]

        if "views" in action:
            action["views"] = form_view + [
                (state, view) for state, view in action["views"] if view != "form"
            ]

        else:
            action["views"] = form_view

        return action
