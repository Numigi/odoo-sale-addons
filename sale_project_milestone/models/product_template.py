# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class ProductTemplate(models.Model):

    _inherit = "product.template"

    service_tracking = fields.Selection(
        selection_add=[
            ("milestone_existing_project", "Create milestone in existing project"),
            ("milestone_new_project", "Create milestone in new project"),
        ]
    )
    milestone_template_id = fields.Many2one(
        "project.milestone",
        string="Milestone Template",
        company_dependent=True,
        copy=True,
    )

    @api.onchange("service_tracking")
    def _onchange_service_tracking(self):
        res = super()._onchange_service_tracking()

        if self.service_tracking == "milestone_existing_project":
            self.project_template_id = False
            self.milestone_template_id = False

        elif self.service_tracking == "milestone_new_project":
            self.project_id = False

        else:
            self.milestone_template_id = False

        return res
