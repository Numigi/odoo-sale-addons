# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _get_partner_restrict_domain(self):
        partner_restrict_domain = super(SaleOrder, self)._get_partner_restrict_domain()
        if self.sale_order_partner_restrict == "affiliate_contact":
            partner_restrict_domain = [
                ("parent_id", "!=", False),
                ("type", "=", "contact")
            ]
        return partner_restrict_domain
