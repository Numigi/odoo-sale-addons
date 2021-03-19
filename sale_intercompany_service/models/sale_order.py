# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    is_interco_service = fields.Boolean(
        readonly=True, states={"draft": [("readonly", False)]}
    )

    def open_interco_service_invoice_wizard(self):
        return self._get_interco_service_wizard_action("invoice")

    def open_interco_service_summary(self):
        return self._get_interco_service_wizard_action("seller_summary")

    def _get_interco_service_wizard_action(self, mode):
        wizard = self.env["sale.interco.service.invoice"].create(
            {"order_id": self.id, "mode": mode}
        )
        action = wizard.get_formview_action()
        action["view_id"] = self.env.ref("sale_intercompany_service.seller_wizard").id
        action["target"] = "new"
        return action
