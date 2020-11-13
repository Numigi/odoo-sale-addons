# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    def get_available_payment_acquirers(self):
        partners = self | self.commercial_partner_id
        privilege_level_acquirers = partners.mapped(
            "privilege_level_id.payment_acquirer_ids"
        )
        unfiltered_acquirers = self.env["payment.acquirer"].search(
            [("privilege_level_ids", "=", False)]
        )
        return privilege_level_acquirers | unfiltered_acquirers
