from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm


class WebsiteFormCrmTeam(WebsiteForm):
    def insert_record(self, request_obj, model, values, custom, meta=None):
        record_id = super().insert_record(request_obj, model, values, custom, meta=meta)

        if self._is_crm_lead_model(model) and record_id:
            self._assign_default_sales_team(record_id)

        return record_id

    def _assign_default_sales_team(self, lead_id):
        sales_team = self._find_sales_team()
        lead = self._get_lead(lead_id)

        if sales_team and lead:
            lead.write({"team_id": sales_team.id})

    def _is_crm_lead_model(self, model):
        return model.sudo().model == "crm.lead"

    def _find_sales_team(self):
        return request.env["crm.team"].sudo().search(
            ["|", ("name", "=", "Équipe ventes"), ("name", "=", "Sales Team")],
            limit=1,
        )

    def _get_lead(self, lead_id):
        lead = request.env["crm.lead"].sudo().browse(lead_id)
        return lead if lead.exists() else None