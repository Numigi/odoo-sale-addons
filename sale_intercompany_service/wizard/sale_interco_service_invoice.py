# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleIntercoServiceInvoice(models.TransientModel):

    _name = "sale.interco.service.invoice"
    _description = "Sale Interco Service Invoice"

    order_id = fields.Many2one("sale.order")

    company_id = fields.Many2one("res.company", related="order_id.company_id")
    discount = fields.Float(
        related="company_id.interco_service_discount", related_sudo=True
    )

    interco_company_id = fields.Many2one(
        "res.company", compute="_compute_interco_company_id"
    )
    interco_partner_id = fields.Many2one(
        "res.partner", compute="_compute_interco_partner_id"
    )
    interco_position_id = fields.Many2one(
        "account.fiscal.position",
        compute="_compute_interco_position_id",
        compute_sudo=True,
    )

    customer_id = fields.Many2one("res.partner", related="order_id.partner_id")
    customer_position_id = fields.Many2one(
        "account.fiscal.position",
        compute="_compute_customer_position_id",
        compute_sudo=True,
    )
    customer_position_name = fields.Char(
        related="customer_position_id.display_name", related_sudo=True
    )
    customer_delivery_address_id = fields.Many2one(
        "res.partner", related="order_id.partner_shipping_id"
    )

    @api.depends("interco_partner_id")
    def _compute_interco_company_id(self):
        for wizard in self:
            wizard.interco_company_id = wizard.sudo()._get_interco_company()

    def _get_interco_company(self):
        partner = self.interco_partner_id.commercial_partner_id
        return self.env["res.company"].search(
            [("partner_id", "=", partner.id)], limit=1
        )

    @api.depends("interco_partner_id")
    def _compute_interco_position_id(self):
        for wizard in self:
            wizard.interco_position_id = wizard.sudo()._get_interco_position()

    def _get_interco_position(self):
        return (
            self.env["account.fiscal.position"]
            .with_context(force_company=self.company_id.id)
            .get_fiscal_position(self.interco_partner_id.id)
        )

    def _compute_customer_position_id(self):
        for wizard in self:
            wizard.customer_position_id = wizard.sudo()._get_customer_position()

    def _get_customer_position(self):
        return (
            self.env["account.fiscal.position"]
            .with_context(force_company=self.interco_company_id.id)
            .get_fiscal_position(
                self.customer_id.id, self.customer_delivery_address_id.id
            )
        )

    def _compute_interco_partner_id(self):
        for wizard in self:
            wizard.interco_partner_id = wizard.sudo().order_id.partner_invoice_id

    def validate(self):
        invoice_ids = self.order_id.action_invoice_create()
        invoices = self.env["account.invoice"].browse(invoice_ids)

        for invoice in invoices:
            self._update_invoice(invoice)

        return invoices[:1].get_formview_action()

    def _update_invoice(self, invoice):
        invoice.partner_shipping_id = self.interco_partner_id.id
        self._update_invoice_line_discount(invoice)

    def _update_invoice_line_discount(self, invoice):
        for line in invoice.invoice_line_ids:
            line.discount = 100 * (
                1 - (1 - line.discount / 100) * (1 - self.discount / 100)
            )
