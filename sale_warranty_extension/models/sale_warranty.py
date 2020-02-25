# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleWarranty(models.Model):

    _inherit = 'sale.warranty'

    use_warranty_extension = fields.Boolean(track_visibility='onchange')
    extension_start_date = fields.Date(track_visibility='onchange', copy=False)
    extension_expiry_date = fields.Date(track_visibility='onchange', copy=False)
    extension_template_id = fields.Many2one(related='type_id.extension_template_id')
    extension_subscription_id = fields.Many2one(
        'sale.subscription',
        'Extension Contract',
        ondelete='restrict',
    )

    @api.onchange('activation_date', 'type_id', 'use_warranty_extension')
    def _onchange_activation_date_set_extension_dates(self):
        """When the activation date is manually set, compute automatically the extension dates."""
        if self.activation_date and self.type_id and self.use_warranty_extension:
            extension_start = (
                self.activation_date +
                relativedelta(months=self.type_id.duration_in_months)
            )
            extension_expiry = (
                extension_start +
                relativedelta(months=self.type_id.extension_duration_in_months)
            )
            self.extension_start_date = extension_start
            self.extension_expiry_date = extension_expiry

        else:
            self.extension_start_date = False
            self.extension_expiry_date = False
            self.extension_subscription_id = False

    @api.constrains('extension_start_date', 'extension_expiry_date')
    def _check_extension_start_prior_to_expiry(self):
        for warranty in self:
            if (
                warranty.extension_start_date and warranty.extension_expiry_date and
                warranty.extension_start_date > warranty.extension_expiry_date
            ):
                raise ValidationError(_(
                    "The extension start date ({extension_start_date}) "
                    "of the warranty ({warranty}) "
                    "must be prior to the extension expiry ({extension_expiry_date})."
                ).format(
                    extension_start_date=warranty.extension_start_date,
                    extension_expiry_date=warranty.extension_expiry_date,
                    warranty=warranty.display_name,
                ))

    def find_warranties_to_set_expired(self):
        """Filter warranties to end based on the extension date.

        If the warranty has an extension and that the extension
        is not expired, then the warranty is kept active.
        """
        expired_warranties = super().find_warranties_to_set_expired()
        today = datetime.now().date()
        return expired_warranties.filtered(
            lambda w: (
                not w.use_warranty_extension or
                not w.extension_expiry_date or
                w.extension_expiry_date < today
            )
        )

    def action_activate(self, serial_number=None):
        """Extend the warranty on activation if it meets the requirements.

        In order to extend the warranty:
            1- The use_warranty_extension checkbox must be checked.
            2- The customer must have an active subscription.
            3- This subscription must have the subscription
               template defined on the warranty type.
        """
        super().action_activate(serial_number)
        if self._should_be_extended():
            contract = self._get_active_extension_subscription()
            self.write({
                'use_warranty_extension': True,
                'extension_start_date': self._get_extension_start_date(),
                'extension_expiry_date': self._get_extension_expiry_date(),
                'extension_subscription_id': contract.id,
            })

    def _get_active_extension_subscription(self):
        return self.env['sale.subscription'].search([
            ('in_progress', '=', True),
            ('partner_id.commercial_partner_id', '=',
                self.partner_id.commercial_partner_id.id),
            ('template_id', '=', self.type_id.extension_template_id.id),
        ], limit=1)

    def _should_be_extended(self):
        return (
            self.type_id.use_warranty_extension and
            bool(self._get_active_extension_subscription())
        )

    def _get_extension_start_date(self):
        return self.expiry_date + timedelta(1)

    def _get_extension_expiry_date(self):
        return self.expiry_date + relativedelta(months=self.type_id.extension_duration_in_months)
