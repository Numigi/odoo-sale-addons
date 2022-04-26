# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


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
        index=True,
        domain=[("sale_line_id", "=", False)],
    )

    @api.onchange("service_tracking")
    def _onchange_service_tracking(self):
        res = super(ProductTemplate, self)._onchange_service_tracking()
        res = res if res is not None else {}
        service_tracking = self.service_tracking

        if service_tracking == "milestone_existing_project":
            self.update({"project_template_id": False, "milestone_template_id": False})

        elif service_tracking == "milestone_new_project":
            self.project_id = False
            res["domain"] = {
                "milestone_template_id": [
                    ("sale_line_id", "=", False),
                    ("project_id", "=", False),
                    "|",
                    ("sale_line_id", "=", False),
                    ("project_id.billable_type", "=", "no"),
                ]
            }

        else:
            self.milestone_template_id = False

        return res

    @api.onchange("project_template_id", "milestone_template_id")
    def _onchange_template_project_milestone(self):

        if self.project_template_id and self.milestone_template_id:
            raise ValidationError(
                _("You can't select simultaneously project template and milestone template.")
            )
