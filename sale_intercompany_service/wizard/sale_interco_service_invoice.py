# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models
from odoo.exceptions import AccessError

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
        "account.move", compute="_compute_related_invoices", compute_sudo=True
    )
    interco_invoice_names = fields.Text(
        compute="_compute_related_invoices", compute_sudo=True
    )
    supplier_invoice_ids = fields.Many2many(
        "account.move", compute="_compute_related_invoices", compute_sudo=True
    )
    supplier_invoice_names = fields.Text(
        compute="_compute_related_invoices", compute_sudo=True
    )
    customer_invoice_ids = fields.Many2many(
        "account.move", compute="_compute_related_invoices", compute_sudo=True
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
            .with_company(self.company_id)
            .get_fiscal_position(self.interco_partner_id.id)
        )

    @api.depends("supplier_partner_id")
    def _compute_supplier_position_id(self):
        for wizard in self:
            wizard.supplier_position_id = wizard.sudo()._get_supplier_position()

    def _get_supplier_position(self):
        return (
            self.env["account.fiscal.position"]
            .with_company(self.interco_company_id)
            .get_fiscal_position(self.supplier_partner_id.id)
        )

    def _compute_customer_position_id(self):
        for wizard in self:
            wizard.customer_position_id = wizard.sudo()._get_customer_position()

    def _get_customer_position(self):
        return (
            self.env["account.fiscal.position"]
            .with_company(self.interco_company_id)
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
            wizard.interco_invoice_ids = wizard._get_interco_invoices()
            wizard.interco_invoice_names = wizard._format_invoice_names(
                wizard.interco_invoice_ids
            )
            wizard.customer_invoice_ids = wizard.interco_invoice_ids.sudo().mapped(
                "interco_customer_invoice_id"
            )
            wizard.customer_invoice_names = wizard._format_invoice_names(
                wizard.customer_invoice_ids
            )
            wizard.supplier_invoice_ids = wizard.interco_invoice_ids.sudo().mapped(
                "interco_supplier_invoice_id"
            )
            wizard.supplier_invoice_names = wizard._format_invoice_names(
                wizard.supplier_invoice_ids
            )

    def _get_interco_invoices(self):
        return [
            (6, 0, self.order_id.sudo().mapped("order_line.invoice_lines.move_id.id"))
        ]

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
        )._create_invoices()
        return invoice_ids

    def _update_interco_invoice(self, invoice):
        invoice.with_context(check_move_validity=False).write(
            {
                "interco_service_order_id": self.order_id.id,
                "partner_shipping_id": self.interco_partner_id.id,
                "is_interco_service": True,
            }
        )
        self._update_invoice_line_discount(invoice)

        invoice.with_context(
            check_move_validity=False
        ).invoice_line_ids._onchange_mark_recompute_taxes()
        invoice.with_context(check_move_validity=False)._onchange_invoice_line_ids()

    def _update_invoice_line_discount(self, invoice):
        for line in invoice.invoice_line_ids:
            line.with_context(check_move_validity=False).discount = 100 * (
                1 - (1 - line.discount / 100) * (1 - self.discount / 100)
            )

    def _make_supplier_invoice(self, invoice):
        self = (
            self.with_company(self.interco_company_id)
            .with_context(default_currency_id=invoice.currency_id.id)
            .sudo()
        )
        partner = self.company_id.partner_id
        supplier_invoice = self.env["account.move"].create(
            {
                "company_id": self.interco_company_id.id,
                "partner_id": partner.id,
                "move_type": "in_invoice"
                if invoice.move_type == "out_invoice"
                else "in_refund",
                "date": invoice.date,
                "invoice_date": invoice.invoice_date,
                "invoice_line_ids": [
                    (0, 0, vals)
                    for vals in self._get_supplier_invoice_line_vals(invoice)
                ],
                "name": invoice.name,
                "invoice_origin": invoice.invoice_origin,
                "narration": invoice.narration,
                "fiscal_position_id": self.supplier_position_id.id,
                "interco_service_order_id": self.order_id.id,
                "is_interco_service": True,
                "invoice_user_id": None,
            }
        )

        supplier_invoice.with_context(
            check_move_validity=False
        ).invoice_line_ids._onchange_mark_recompute_taxes()

        invoice.interco_supplier_invoice_id = supplier_invoice

    def _get_supplier_invoice_line_vals(self, invoice):
        return [
            self._get_single_supplier_invoice_line_vals(l)
            for l in invoice.invoice_line_ids
        ]

    def _get_single_supplier_invoice_line_vals(self, invoice_line):
        product = invoice_line.product_id.with_company(self.interco_company_id).sudo()

        self = self.with_company(self.interco_company_id).sudo()

        fiscal_position = self.supplier_position_id
        accounts = product.product_tmpl_id.get_product_accounts(
            fiscal_pos=fiscal_position
        )
        account_id = accounts["expense"]
        taxes = (
            product.supplier_taxes_id.filtered(
                lambda r: r.company_id == self.interco_company_id
            )
            or account_id.tax_ids
            or self.interco_company_id.account_purchase_tax_id
        )
        tax_ids = fiscal_position.map_tax(
            taxes, product=product, partner=invoice_line.move_id.partner_id
        )

        return {
            "product_id": product.id,
            "product_uom_id": invoice_line.product_uom_id.id,
            "quantity": invoice_line.quantity,
            "name": invoice_line.name,
            "price_unit": invoice_line.price_unit,
            "tax_ids": [(6, 0, tax_ids.ids)],
            "discount": invoice_line.discount,
            "account_id": account_id.id,
        }

    def _make_customer_invoice(self, invoice):
        self = (
            self.with_company(self.interco_company_id)
            .with_context(default_currency_id=invoice.currency_id.id)
            .sudo()
        )
        partner = self.customer_id
        customer_invoice = self.env["account.move"].create(
            {
                "company_id": self.interco_company_id.id,
                "partner_id": partner.id,
                "partner_shipping_id": self.customer_delivery_address_id.id,
                "move_type": invoice.move_type,
                "date": invoice.date,
                "invoice_date": invoice.invoice_date,
                "invoice_line_ids": [
                    (0, 0, vals)
                    for vals in self._get_customer_invoice_line_vals(invoice)
                ],
                "name": invoice.name,
                "invoice_origin": invoice.invoice_origin,
                "narration": invoice.narration,
                "fiscal_position_id": self.customer_position_id.id,
                "interco_service_order_id": self.order_id.id,
                "is_interco_service": True,
                "invoice_user_id": None,
            }
        )

        customer_invoice.with_context(
            check_move_validity=False
        ).invoice_line_ids._onchange_mark_recompute_taxes()

        invoice.interco_customer_invoice_id = customer_invoice

    def _get_customer_invoice_line_vals(self, invoice):
        return [
            self._get_single_customer_invoice_line_vals(l)
            for l in invoice.invoice_line_ids
        ]

    def _get_single_customer_invoice_line_vals(self, invoice_line):
        product = invoice_line.product_id.with_company(self.interco_company_id).sudo()
        self = self.with_company(self.interco_company_id).sudo()

        fiscal_position = self.customer_position_id
        accounts = product.product_tmpl_id.get_product_accounts(
            fiscal_pos=fiscal_position
        )
        account_id = accounts["income"]
        taxes = (
            product.taxes_id.filtered(lambda r: r.company_id == self.interco_company_id)
            or account_id.tax_ids
            or self.interco_company_id.account_sale_tax_id
        )
        tax_ids = fiscal_position.map_tax(
            taxes, product=product, partner=invoice_line.move_id.partner_id
        )

        return {
            "product_id": product.id,
            "product_uom_id": invoice_line.product_uom_id.id,
            "quantity": invoice_line.quantity,
            "name": invoice_line.name,
            "price_unit": invoice_line.price_unit,
            "tax_ids": [(6, 0, tax_ids.ids)],
            "discount": invoice_line.sale_line_ids[:1].discount,
            "account_id": account_id.id,
        }
