# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("state")
    def _compute_type_name(self):
        for record in self:
            if record.state in ("draft", "sent", "cancel"):
                record.type_name = _("Quotation")
            elif record.is_rental is True:
                record.type_name = _("Rental")
            else:
                record.type_name = _("Sales Order")
