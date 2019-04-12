# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WarrantyType(models.Model):

    _name = 'sale.warranty.type'
    _description = 'Sale Warranty Type'

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda s: s.env.user.company_id
    )
    name = fields.Char(required=True)
    duration_in_months = fields.Integer(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)


class Warranty(models.Model):

    _name = 'sale.warranty'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sale Warranty'
    _rec_name = 'reference'

    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.user.company_id,
        track_visibility='onchange',
    )
    partner_id = fields.Many2one(
        'res.partner', 'Customer', required=True, index=True,
        track_visibility='onchange', ondelete='restrict',
    )
    type_id = fields.Many2one(
        'sale.warranty.type', 'Warranty Type', required=True, index=True,
        track_visibility='onchange', ondelete='restrict',
    )
    state = fields.Selection([
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], required=True, default='pending', track_visibility='onchange', copy=False)
    reference = fields.Char(track_visibility='onchange', copy=False)
    activation_date = fields.Date(
        track_visibility='onchange',
        copy=False
    )
    expiry_date = fields.Date(
        track_visibility='onchange',
        copy=False
    )
    sale_order_id = fields.Many2one(
        'sale.order', 'Order', index=True, ondelete='restrict',
        track_visibility='onchange',
        copy=False
    )
    sale_order_line_id = fields.Many2one(
        'sale.order.line', 'Order Line', index=True, ondelete='restrict',
        copy=False
    )
    product_id = fields.Many2one(
        'product.product', 'Product', index=True, ondelete='restrict',
        track_visibility='onchange',
    )
    lot_id = fields.Many2one(
        'stock.production.lot', 'Serial Number', index=True, ondelete='restrict',
        track_visibility='onchange',
        copy=False,
    )
    description = fields.Text(track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('sale.warranty')
        return super().create(vals)

    @api.onchange('activation_date', 'type_id')
    def _onchange_activation_date_set_expiry_date(self):
        """When the activation date is manually set, compute automatically the expiry date."""
        if self.activation_date and self.type_id:
            self.expiry_date = (
                self.activation_date +
                relativedelta(months=self.type_id.duration_in_months) - timedelta(1)
            )

    @api.constrains('activation_date', 'expiry_date')
    def _check_activation_prior_to_expiry(self):
        for warranty in self:
            if (
                warranty.activation_date and warranty.expiry_date and
                warranty.activation_date > warranty.expiry_date
            ):
                raise ValidationError(_(
                    "The activation date ({activation_date}) of the warranty ({warranty}) "
                    "must be prior to its expiry date ({expiry_date})."
                ).format(
                    activation_date=warranty.activation_date,
                    expiry_date=warranty.expiry_date,
                    warranty=warranty.display_name,
                ))

    def action_activate(self):
        self.write({'state': 'active'})

    def action_set_to_pending(self):
        self.write({'state': 'pending'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class ProductTemplateWithWarranty(models.Model):

    _inherit = 'product.template'

    warranty_type_ids = fields.Many2many(
        'sale.warranty.type',
        'product_template_warranty_type_rel',
        'product_id',
        'warranty_type_id',
        'Warranties',
    )

    @api.constrains('warranty_type_ids', 'tracking')
    def _check_if_has_warranties_then_is_serialized(self):
        invalid_products = self.filtered(
            lambda p: p.warranty_type_ids and not p.tracking == 'serial'
        )
        if invalid_products:
            raise ValidationError(_(
                'A product must be tracked by unique serial number in order to support warranties. '
                'You may activate serial numbers for a product in the `Inventory` tab '
                'under `Traceability`.'
            ))


class SaleOrderWithWarrantiesSmartButton(models.Model):

    _inherit = 'sale.order'

    warranty_ids = fields.One2many(
        'sale.warranty',
        'sale_order_id',
        'Warranties',
    )

    warranty_count = fields.Integer(
        compute='_compute_warranty_count'
    )

    @api.multi
    def _compute_warranty_count(self):
        for order in self:
            warranties_not_cancelled = order.warranty_ids.filtered(lambda w: w.state != 'cancelled')
            order.warranty_count = len(warranties_not_cancelled)


class SaleOrderLineWithWarranties(models.Model):

    _inherit = 'sale.order.line'

    warranty_ids = fields.One2many(
        'sale.warranty',
        'sale_order_line_id',
        'Warranties',
    )
