# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("company_id", "partner_id")
    def _check_partner_authorized_companies(self):
        partner = self.partner_id.sudo().commercial_partner_id

        if not self._is_company_authorized(self.company_id, partner):
            self.partner_id = None
            message = _(
                "The company {company} is not authorized to sell to the customer {customer}. "
                "Please switch to another company or select a different customer."
            ).format(
                company=self.company_id.display_name, customer=partner.display_name
            )
            return {"warning": {"title": _("Warning"), "message": message}}

    def _is_company_authorized(self, company, partner):
        companies = partner.sale_authorized_company_ids
        return not companies or company in companies
