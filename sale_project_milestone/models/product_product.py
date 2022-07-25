# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):

    _inherit = "product.product"

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
