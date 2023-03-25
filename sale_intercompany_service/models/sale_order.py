# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_interco_service = fields.Boolean(
        readonly=True, states={"draft": [("readonly", False)]}, default=False
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
        wizard = (
            self.env["sale.interco.service.invoice"]
            .sudo()
            .create({"order_id": self.id, "mode": mode})
        )
        action = wizard.get_formview_action()
        action["views"] = [
            (self.env.ref(f"sale_intercompany_service.seller_wizard").id, "form")
        ]
        action["res_id"] = wizard.id
        action["target"] = "new"
        return action

    @api.onchange("is_interco_service")
    def _onchange_is_interco_service(self):
        if self.is_interco_service:
            self.partner_invoice_id = False

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        invoice_address = self.partner_invoice_id
        res = super().onchange_partner_id()

        if self.is_interco_service:
            self.partner_invoice_id = invoice_address

        return res

    @api.constrains("is_interco_service", "partner_invoice_id")
    def _check_interco_invoice_partner(self):
        for order in self.filtered("is_interco_service"):
            company = order._get_interco_service_company()
            if not company:
                raise ValidationError(
                    _(
                        "The invoicing address ({partner}) selected on the sale order ({order}) "
                        "is not linked to a company. "
                        "\n\n"
                        "You must select an invoicing address related to a company in order "
                        "to allow the intercompany service."
                    ).format(
                        partner=order.partner_invoice_id.display_name,
                        order=order.display_name,
                    )
                )

    def _get_interco_service_company(self):
        commercial_partner = self.partner_invoice_id.commercial_partner_id
        return (
            self.env["res.company"]
            .sudo()
            .search([("partner_id", "=", commercial_partner.id)], limit=1)
        )

    @api.constrains("partner_id", "partner_invoice_id", "partner_shipping_id")
    def _check_interco_partners_shared_between_companies(self):
        for order in self.filtered("is_interco_service"):
            partners = (
                order.partner_id | order.partner_invoice_id | order.partner_shipping_id
            )
            partners_not_shared = partners.filtered("company_id")
            if partners_not_shared:
                raise ValidationError(
                    _(
                        "The following partners are not shared between companies: {partners}."
                        "\n\n"
                        "The customer, the invoicing address and the delivery address must "
                        "be shared between companies in order "
                        "to allow the intercompany service."
                    ).format(
                        partners=", ".join(partners_not_shared.mapped("display_name"))
                    )
                )

