# -*- coding: utf-8 -*-

from odoo import models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.depends("state")
    def _compute_type_name(self):
        for record in self:
            if record.state in ("draft", "sent", "cancel"):
                record.type_name = _("Quotation")
            elif record.is_rental is True:
                record.type_name = _("Locations")
            else:
                record.type_name = _("Sales Order")
