# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    virtual_2nd_unit_available_at_date = fields.Float(
        compute="_compute_2nd_unit_qty_at_date", digits="Product Second Unit of Measure"
    )
    free_2nd_unit_qty_today = fields.Float(
        compute="_compute_2nd_unit_qty_at_date", digits="Product Second Unit of Measure"
    )
    product_stock_secondary_uom = fields.Char(
        comodel_name='product.secondary.unit',
        related='product_id.stock_secondary_uom_id.name'
    )

    def _set_float_round(self, qty, rounding):
        return float_round(
            qty, precision_rounding=rounding
        )

    def _get_qty_from_factor(self, qty, factor):
        return qty / factor

    @api.depends('virtual_available_at_date', 'free_qty_today')
    def _compute_2nd_unit_qty_at_date(self):
        for line in self:
            if not line.product_id.stock_secondary_uom_id:
                line.virtual_2nd_unit_available_at_date = 0.0
                line.free_2nd_unit_qty_today = 0.0
            else:
                factor = line.product_id.stock_secondary_uom_id.factor or 1.0
                virtual_qty = self._get_qty_from_factor(
                    line.virtual_available_at_date, factor)
                free_qty = self._get_qty_from_factor(
                    line.free_qty_today, factor)
                rounding = line.product_uom.rounding
                line.virtual_2nd_unit_available_at_date = self._set_float_round(
                    virtual_qty, rounding)
                line.free_2nd_unit_qty_today = self._set_float_round(
                    free_qty, rounding)
