# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleIntercoServiceInvoice(models.TransientModel):

    _name = "sale.interco.service.invoice"
    _description = "Sale Interco Service Invoice"

    mode = fields.Selection(
        [("invoice", "Invoice"), ("summary", "Summary")], required=True, readonly=True
    )

    order_id = fields.Many2one("sale.order", readonly=True)
    order_name = fields.Char(
        "Order Name", related="order_id.display_name", related_sudo=True
    )

    company_id = fields.Many2one("res.company", related="order_id.company_id")
    discount = fields.Float(
        related="company_id.interco_service_discount", related_sudo=True
    )

    supplier_partner_id = fields.Many2one(
        "res.partner", related="company_id.partner_id"
    )
    supplier_position_id = fields.Many2one(
        "account.fiscal.position",
        compute="_compute_supplier_position_id",
        compute_sudo=True,
    )
    supplier_position_name = fields.Char(
        "Supplier Position Name",
        related="supplier_position_id.display_name",
        related_sudo=True,
    )

    interco_company_id = fields.Many2one(
        "res.company", compute="_compute_interco_company_id"
    )
    interco_partner_id = fields.Many2one(
        "res.partner", compute="_compute_interco_partner_id"
    )
    interco_invoice_address_id = fields.Many2one(
        "res.partner", related="order_id.partner_invoice_id", related_sudo=True
    )
    interco_position_id = fields.Many2one(
        "account.fiscal.position",
        compute="_compute_interco_position_id",
        compute_sudo=True,
    )
    interco_position_name = fields.Char(
        "Interco Position Name",
        related="interco_position_id.display_name",
        related_sudo=True,
    )

    customer_id = fields.Many2one("res.partner", related="order_id.partner_id")
    customer_position_id = fields.Many2one(
        "account.fiscal.position",
        compute="_compute_customer_position_id",
        compute_sudo=True,
    )
    customer_position_name = fields.Char(
        "Customer Position Name",
        related="customer_position_id.display_name",
        related_sudo=True,
    )
    customer_delivery_address_id = fields.Many2one(
        "res.partner", related="order_id.partner_shipping_id"
    )

    interco_invoice_ids = fields.Many2many(
        "account.invoice", compute="_compute_related_invoices", compute_sudo=True
    )
    interco_invoice_names = fields.Text(
        compute="_compute_related_invoices", compute_sudo=True
    )
    supplier_invoice_ids = fields.Many2many(
        "account.invoice", compute="_compute_related_invoices", compute_sudo=True
    )
    supplier_invoice_names = fields.Text(
        compute="_compute_related_invoices", compute_sudo=True
    )
    customer_invoice_ids = fields.Many2many(
        "account.invoice", compute="_compute_related_invoices", compute_sudo=True
    )
    customer_invoice_names = fields.Text(
        compute="_compute_related_invoices", compute_sudo=True
    )

    @api.depends("interco_partner_id")
    def _compute_interco_company_id(self):
        for wizard in self:
            wizard.interco_company_id = wizard.sudo()._get_interco_company()

    def _get_interco_company(self):
        return self.env["res.company"].search(
            [("partner_id", "=", self.interco_partner_id.id)], limit=1
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

    @api.depends("supplier_partner_id")
    def _compute_supplier_position_id(self):
        for wizard in self:
            wizard.supplier_position_id = wizard.sudo()._get_supplier_position()

    def _get_supplier_position(self):
        return (
            self.env["account.fiscal.position"]
            .with_context(force_company=self.interco_company_id.id)
            .get_fiscal_position(self.supplier_partner_id.id)
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
            wizard.interco_partner_id = (
                wizard.sudo().interco_invoice_address_id.commercial_partner_id
            )

    def _compute_related_invoices(self):
        for wizard in self:
            self.interco_invoice_ids = self._get_interco_invoices()
            self.interco_invoice_names = self._format_invoice_names(
                self.interco_invoice_ids
            )
            self.customer_invoice_ids = self.interco_invoice_ids.sudo().mapped(
                "interco_customer_invoice_id"
            )
            self.customer_invoice_names = self._format_invoice_names(
                self.customer_invoice_ids
            )
            self.supplier_invoice_ids = self.interco_invoice_ids.sudo().mapped(
                "interco_supplier_invoice_id"
            )
            self.supplier_invoice_names = self._format_invoice_names(
                self.supplier_invoice_ids
            )

    def _get_interco_invoices(self):
        return self.order_id.sudo().mapped("order_line.invoice_lines.invoice_id")

    def _format_invoice_names(self, invoices):
        return "\n".join(invoices.sudo().mapped("display_name"))

    def validate(self):
        invoices = self._create_interco_invoice()

        for invoice in invoices:
            self._update_interco_invoice(invoice)
            self._make_supplier_invoice(invoice)
            self._make_customer_invoice(invoice)

        return invoices[:1].get_formview_action()

    def _create_interco_invoice(self):
        invoice_ids = self.order_id.with_context(
            default_currency_id=self.order_id.currency_id.id
        ).action_invoice_create()
        return self.env["account.invoice"].browse(invoice_ids)

    def _update_interco_invoice(self, invoice):
        invoice.write(
            {
                "interco_service_order_id": self.order_id.id,
                "partner_shipping_id": self.interco_partner_id.id,
                "is_interco_service": True,
            }
        )
        self._update_invoice_line_discount(invoice)

    def _update_invoice_line_discount(self, invoice):
        for line in invoice.invoice_line_ids:
            line.discount = 100 * (
                1 - (1 - line.discount / 100) * (1 - self.discount / 100)
            )

    def _make_supplier_invoice(self, invoice):
        self = self.with_context(
            force_company=self.interco_company_id.id,
            company_id=self.interco_company_id.id,
            default_currency_id=invoice.currency_id.id,
        ).sudo()
        partner = self.company_id.partner_id
        supplier_invoice = self.env["account.invoice"].create(
            {
                "company_id": self.interco_company_id.id,
                "partner_id": partner.id,
                "type": "in_invoice" if invoice.type == "out_invoice" else "in_refund",
                "date": invoice.date,
                "date_invoice": invoice.date_invoice,
                "invoice_line_ids": [
                    (0, 0, vals)
                    for vals in self._get_supplier_invoice_line_vals(invoice)
                ],
                "name": invoice.name,
                "origin": invoice.origin,
                "comment": invoice.comment,
                "account_id": partner.property_account_payable_id.id,
                "fiscal_position_id": self.supplier_position_id.id,
                "interco_service_order_id": self.order_id.id,
                "is_interco_service": True,
            }
        )

        for line in supplier_invoice.invoice_line_ids:
            self._set_supplier_taxes(line)

        supplier_invoice.compute_taxes()

        invoice.interco_supplier_invoice_id = supplier_invoice

    def _get_supplier_invoice_line_vals(self, invoice):
        return [
            self._get_single_supplier_invoice_line_vals(l)
            for l in invoice.invoice_line_ids
        ]

    def _get_single_supplier_invoice_line_vals(self, invoice_line):
        product = invoice_line.product_id.with_context(
            force_company=self.interco_company_id.id,
            company_id=self.interco_company_id.id,
        ).sudo()
        account = self.env["account.invoice.line"].get_invoice_line_account(
            "in_invoice", product, self.supplier_position_id, self.interco_company_id
        )
        return {
            "product_id": product.id,
            "uom_id": invoice_line.uom_id.id,
            "quantity": invoice_line.quantity,
            "name": invoice_line.name,
            "price_unit": invoice_line.price_unit,
            "discount": invoice_line.discount,
            "account_id": account.id,
        }

    def _make_customer_invoice(self, invoice):
        self = self.with_context(
            force_company=self.interco_company_id.id,
            company_id=self.interco_company_id.id,
            default_currency_id=invoice.currency_id.id,
        ).sudo()
        partner = self.customer_id
        customer_invoice = self.env["account.invoice"].create(
            {
                "company_id": self.interco_company_id.id,
                "partner_id": partner.id,
                "partner_shipping_id": self.customer_delivery_address_id.id,
                "type": invoice.type,
                "date": invoice.date,
                "date_invoice": invoice.date_invoice,
                "invoice_line_ids": [
                    (0, 0, vals)
                    for vals in self._get_customer_invoice_line_vals(invoice)
                ],
                "name": invoice.name,
                "origin": invoice.origin,
                "comment": invoice.comment,
                "account_id": partner.property_account_receivable_id.id,
                "fiscal_position_id": self.customer_position_id.id,
                "interco_service_order_id": self.order_id.id,
                "is_interco_service": True,
            }
        )

        for line in customer_invoice.invoice_line_ids:
            self._set_customer_taxes(line)

        customer_invoice.compute_taxes()

        invoice.interco_customer_invoice_id = customer_invoice

    def _set_customer_taxes(self, invoice_line):
        invoice = invoice_line.invoice_id
        product = invoice_line.product_id
        taxes = (
            product.taxes_id.filtered(lambda r: r.company_id == invoice.company_id)
            or invoice_line.account_id.tax_ids
            or invoice.company_id.account_sale_tax_id
        )
        invoice_line.invoice_line_tax_ids = invoice.fiscal_position_id.map_tax(
            taxes, product, invoice.partner_id
        )

    def _set_supplier_taxes(self, invoice_line):
        invoice = invoice_line.invoice_id
        product = invoice_line.product_id
        taxes = (
            product.supplier_taxes_id.filtered(
                lambda r: r.company_id == invoice.company_id
            )
            or invoice_line.account_id.tax_ids
            or invoice.company_id.account_purchase_tax_id
        )
        invoice_line.invoice_line_tax_ids = invoice.fiscal_position_id.map_tax(
            taxes, product, invoice.partner_id
        )

    def _get_customer_invoice_line_vals(self, invoice):
        return [
            self._get_single_customer_invoice_line_vals(l)
            for l in invoice.invoice_line_ids
        ]

    def _get_single_customer_invoice_line_vals(self, invoice_line):
        product = invoice_line.product_id.with_context(
            force_company=self.interco_company_id.id,
            company_id=self.interco_company_id.id,
        ).sudo()
        account = self.env["account.invoice.line"].get_invoice_line_account(
            "out_invoice", product, self.customer_position_id, self.interco_company_id
        )
        return {
            "product_id": product.id,
            "uom_id": invoice_line.uom_id.id,
            "quantity": invoice_line.quantity,
            "name": invoice_line.name,
            "price_unit": invoice_line.price_unit,
            "discount": invoice_line.sale_line_ids[:1].discount,
            "account_id": account.id,
        }
