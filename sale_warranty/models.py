# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class WarrantyType(models.Model):

    _name = 'sale.warranty.type'
    _description = 'Sale Warranty Type'

    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
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
    ], required=True, default='pending', track_visibility='onchange')
    reference = fields.Char(track_visibility='onchange')
    activation_date = fields.Date(track_visibility='onchange')
    expiry_date = fields.Date(track_visibility='onchange')
    sale_order_id = fields.Many2one(
        'sale.order', 'Order', index=True, ondelete='restrict',
        track_visibility='onchange',
    )
    sale_order_line_id = fields.Many2one(
        'sale.order.line', 'Order Line', index=True, ondelete='restrict',
    )
    product_id = fields.Many2one(
        'product.product', 'Product', index=True, ondelete='restrict',
        track_visibility='onchange',
    )
    lot_id = fields.Many2one(
        'stock.production.lot', 'Serial Number', index=True, ondelete='restrict',
        track_visibility='onchange',
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
                relativedelta(months=self.type_id.duration_in_months)
            )

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
