# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleTarget(models.Model):

    _name = "sale.target"
    _description = "Sale Target"
    _rec_name = 'date_start'
    _order = 'date_start desc'

    date_start = fields.Date("Start date", required=True)
    date_end = fields.Date("End date", required=True)
    partner_id = fields.Many2one(
        string="Partner", comodel_name="res.partner", ondelete="cascade", required=True
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        string="Company Currency",
        readonly=True,
        related="partner_id.currency_id",
    )
    sale_target = fields.Monetary(
        "Sale target", currency_field="company_currency_id", required=True
    )
    realized_target = fields.Monetary(
        "Realized target",
        currency_field="company_currency_id",
        compute="_compute_realized_target",
    )
    realized = fields.Float("Realized %", compute="_compute_realized")
    is_old_sale_target = fields.Boolean(
        "Is old sale target", compute="_compute_is_old_sale_target"
    )

    _sql_constraints = [
        ('check_date_overlap', 'CHECK(date_start <= date_end)',
         _('The start date must be before the end date.'))
    ]

    @api.constrains('date_start', 'date_end')
    def _check_sale_target_date_overlap(self):
        """Only one sales target is allowed for a period.
        If a user creates 2 sales targets for 2 overlapping periods,
        then a validation error message is displayed"""
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('partner_id', '=', rec.partner_id.id),
                '|',
                '&', ('date_start', '<=', rec.date_start),
                ('date_end', '>=', rec.date_start),
                '&', ('date_start', '<=', rec.date_end),
                ('date_end', '>=', rec.date_end)
            ]
            overlapping_periods = self.search(domain)
            if overlapping_periods:
                raise ValidationError(
                    _('You cannot create 2 Sales Target overlapping.')
                )

    def _compute_realized_target(self):
        """The value of this field is based on confirmed customer orders
        It is the order confirmation date which is used to associate the
        sale within the period of a sales objective. The calculation is
        based on the total amount excluding taxes of the sale."""
        for rec in self:
            amount_untaxed = 0.0
            if rec.partner_id.is_sale_target_allowed_contact:
                datetime_start = fields.Datetime.to_datetime(rec.date_start)
                datetime_end = fields.Datetime.to_datetime(rec.date_end)
                confirmed_orders = rec.partner_id.sale_order_ids.filtered(
                    lambda o: o.state in ("sale", "done")
                    and o.date_order <= datetime_end
                    and o.date_order >= datetime_start
                )
                amount_untaxed = sum(confirmed_orders.mapped("amount_untaxed"))
            rec.realized_target = amount_untaxed

    def _compute_realized(self):
        for rec in self:
            rec.realized = (rec.realized_target / rec.sale_target) \
                if rec.partner_id.is_sale_target_allowed_contact and \
                rec.sale_target else 0.0

    def _compute_is_old_sale_target(self):
        for rec in self:
            rec.is_old_sale_target = \
                True if rec.partner_id.is_sale_target_allowed_contact and \
                rec.date_end < fields.Date.today() else False
