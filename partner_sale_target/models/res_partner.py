# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, _, api
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_target_ids = fields.One2many(
        'sale.target',
        'partner_id',
        string='Sale target',
    )
    current_sale_target = fields.Monetary(
        string='Current Sale target',
        currency_field='currency_id',
        compute='_compute_current_sale_target'
    )
    current_realized_target = fields.Float(
        string='% Realized current period',
        currency_field='currency_id',
        compute='_compute_current_sale_target'
    )

    is_sale_target_allowed_contact = fields.Boolean(
        'Is sale target allowed contact',
        compute='_compute_is_sale_target_allowed_contact'
    )

    def _compute_is_sale_target_allowed_contact(self):
        """ Target calculated only on an Individual contact not associated with
          a parent contact of type Company, or on a contact of type Company."""
        for rec in self:
            if (rec.company_type == 'person' and
                (not rec.parent_id or
                 rec.parent_id.company_type != 'company')) or \
                    rec.company_type == 'company':
                rec.is_sale_target_allowed_contact = True
            else:
                rec.is_sale_target_allowed_contact = False

    def get_current_sale_targets(self):
        self.ensure_one()
        return self.sale_target_ids.filtered(
                lambda o: o.date_start <= fields.Date.today() and
                o.date_end >= fields.Date.today())

    def _compute_current_sale_target(self):
        for rec in self:
            target_ids = rec.get_current_sale_targets()
            rec.current_sale_target = sum(target_ids.mapped('sale_target'))
            _logger.info(target_ids.mapped('realized'))
            rec.current_realized_target = sum(target_ids.mapped('realized'))

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id and self.sale_target_ids and\
                self.company_type == 'person':
            return {'warning': {
                'title': _("Warning"),
                'message': _('Please note that the Sales Targets will be '
                             'deleted, Sales Targets will be managed on '
                             'the commercial entity.'
                             ),
            }}

    def write(self, vals):
        if "parent_id" in vals and vals["parent_id"]:
            if not self.parent_id and self.sale_target_ids and\
                            self.company_type == 'person':
                self.sale_target_ids.unlink()
        return super().write(vals)
