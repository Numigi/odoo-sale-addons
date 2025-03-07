# Copyright 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def action_view_milestone(self):
        res = super().action_view_milestone()
        res["views"] = [
            (False, "tree"),
            (self.env.ref("project.project_milestone_view_form").id, "form"),
        ]
        res["view_mode"] = "form"
        return res
