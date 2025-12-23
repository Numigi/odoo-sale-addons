# -*- coding: utf-8 -*-
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0).

from odoo.addons.website_crm.controllers.main import WebsiteForm


class WebsiteForm(WebsiteForm):
    def insert_record(self, request, model, values, custom, meta=None):
        if model.model == "crm.lead":
            values["team_id"] = request.env.ref(
                "numigi_test_crm_ELSAILI.sales_crm_team"
            ).id
        return super(WebsiteForm, self).insert_record(
            request, model, values, custom, meta=meta
        )
