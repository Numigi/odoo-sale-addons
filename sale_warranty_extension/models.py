# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class SaleWarrantyType(models.Model):

    _inherit = 'sale.warranty.type'

    use_warranty_extension = fields.Boolean()
    extension_duration_in_months = fields.Integer()
    extension_template_id = fields.Many2one(
        'sale.subscription.template',
        'Extension Subscription Template',
        ondelete='restrict',
    )


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
