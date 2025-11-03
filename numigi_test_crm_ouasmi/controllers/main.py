from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm as WebsiteFormController


# ================================================================
# 7-
# ================================================================
class WebsiteForm(WebsiteFormController):
    def insert_record(self, request, model, values, custom, meta=None):
        is_lead_model = model.model == "crm.lead"
        if is_lead_model:
            team = request.env["crm.team"].sudo().search([("name", "=", "Équipe Ventes")], limit=1)
            if team:
                values["team_id"] = team.id

        result = super(WebsiteForm, self).insert_record(request, model, values, custom, meta=meta)

        if is_lead_model:
            visitor_sudo = request.env["website.visitor"]._get_visitor_from_request()
            if visitor_sudo and result:
                lead_sudo = request.env["crm.lead"].browse(result).sudo()
                if lead_sudo.exists():
                    vals = {"lead_ids": [(4, result)]}
                    if not visitor_sudo.lead_ids and not visitor_sudo.partner_id:
                        vals["name"] = lead_sudo.contact_name
                    visitor_sudo.write(vals)
        return result
