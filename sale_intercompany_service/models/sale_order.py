# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class SaleOrder(models.Model):

    _inherit = "sale.order"

    is_interco_service = fields.Boolean(
        readonly=True, states={"draft": [("readonly", False)]}
    )

    def open_interco_service_invoice_wizard(self):
        action = self._get_interco_service_wizard_action("invoice")
        action["name"] = _("Invoice Interco Service")
        return action

    def open_interco_service_summary(self):
        action = self._get_interco_service_wizard_action("summary")
        action["name"] = _("Interco Service")
        return action

    def _get_interco_service_wizard_action(self, mode):
        wizard = self.env["sale.interco.service.invoice"].create(
            {"order_id": self.id, "mode": mode}
        )
        action = wizard.get_formview_action()
        action["views"] = [
            (self.env.ref(f"sale_intercompany_service.seller_wizard").id, "form")
        ]
        action["target"] = "new"
        return action

    @api.onchange("is_interco_service")
    def _onchange_is_interco_service(self):
        if self.is_interco_service:
            self.partner_invoice_id = False
