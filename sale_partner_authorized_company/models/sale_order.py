# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.onchange("company_id", "partner_id")
    def _check_partner_authorized_companies(self):
        commercial_partner = self.partner_id.sudo().commercial_partner_id
        companies = commercial_partner.sale_authorized_company_ids

        if companies and self.company_id not in companies:
            self.partner_id = None
            message = _(
                "The company {company} is not authorized to sell to the customer {customer}. "
                "Please switch to another company or select a different customer."
            ).format(
                company=self.company_id.display_name,
                customer=commercial_partner.display_name,
            )
            return {"warning": {"title": _("Warning"), "message": message}}
