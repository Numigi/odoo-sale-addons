# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Warranty(models.Model):

    _name = "sale.warranty"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Sale Warranty"
    _rec_name = "reference"

    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda s: s.env.user.company_id,
        tracking=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Customer",
        required=True,
        index=True,
        tracking=True,
        ondelete="restrict",
    )
    type_id = fields.Many2one(
        "sale.warranty.type",
        "Warranty Type",
        required=True,
        index=True,
        tracking=True,
        ondelete="restrict",
    )
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("active", "Active"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="pending",
        tracking=True,
        copy=False,
    )
    reference = fields.Char(tracking=True, copy=False)
    activation_date = fields.Date(tracking=True, copy=False)
    expiry_date = fields.Date(tracking=True, copy=False)
    sale_order_id = fields.Many2one(
        "sale.order",
        "Order",
        index=True,
        ondelete="cascade",
        tracking=True,
        copy=False,
    )
    sale_order_line_id = fields.Many2one(
        "sale.order.line", "Order Line", index=True, ondelete="cascade", copy=False
    )
    product_id = fields.Many2one(
        "product.product",
        "Product",
        index=True,
        ondelete="restrict",
        tracking=True,
    )
    lot_id = fields.Many2one(
        "stock.production.lot",
        "Serial Number",
        index=True,
        ondelete="restrict",
        tracking=True,
        copy=False,
    )
    description = fields.Text(tracking=True)

    @api.model
    def create(self, vals):
        vals["reference"] = self.env["ir.sequence"].next_by_code("sale.warranty")
        return super().create(vals)

    @api.onchange("activation_date", "type_id")
    def _onchange_activation_date_set_expiry_date(self):
        """When the activation date is manually set, compute automatically the expiry date."""
        if self.activation_date and self.type_id:
            self.expiry_date = (
                self.activation_date
                + relativedelta(months=self.type_id.duration_in_months)
                - timedelta(1)
            )

    @api.constrains("activation_date", "expiry_date")
    def _check_activation_prior_to_expiry(self):
        for warranty in self:
            if (
                warranty.activation_date
                and warranty.expiry_date
                and warranty.activation_date > warranty.expiry_date
            ):
                raise ValidationError(
                    _(
                        "The activation date ({activation_date}) of the warranty ({warranty}) "
                        "must be prior to its expiry date ({expiry_date})."
                    ).format(
                        activation_date=warranty.activation_date,
                        expiry_date=warranty.expiry_date,
                        warranty=warranty.display_name,
                    )
                )

    def expired_warranties_cron(self):
        """Update the state of warranties that are expired."""
        warranties_to_end = self.find_warranties_to_set_expired()
        warranties_to_end.action_set_expired()

    def find_warranties_to_set_expired(self):
        return self.env["sale.warranty"].search(
            [("state", "=", "active"), ("expiry_date", "<", datetime.now().date())]
        )

    def action_activate(self, serial_number=None):
        """Activate the warranty.

        :param serial_number: the stock.production.lot to link to the warranty
        """
        today = datetime.now().date()
        expiry_date = (
            today + relativedelta(months=self.type_id.duration_in_months) - timedelta(1)
        )
        self.write(
            {
                "state": "active",
                "lot_id": serial_number.id if serial_number else None,
                "expiry_date": expiry_date,
                "activation_date": today,
            }
        )

    def action_set_to_pending(self):
        self.write({"state": "pending"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_set_expired(self):
        self.write({"state": "expired"})
