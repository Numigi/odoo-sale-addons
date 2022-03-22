# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.onchange("is_rental", "partner_id")
    def onchange_partner_id(self):
        super().onchange_partner_id()
        if self.is_rental:
            self.pricelist_id = self.partner_id.rental_pricelist_id
