# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
import logging
from collections import defaultdict

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_available_color = fields.Char(
        "Qty Available Color",
        compute="_compute_qty_available_color",
        help="​Green == Only available in the default warehouse "
        "Yellow == Partially available in the warehouse by default "
        "​Red == Not available in warehouse by default"
        )
    qty_reserved = fields.Float(
        "Qty Reserved",
        compute="_get_reserved_qty"
        )
    virtual_available_at_date = fields.Float(compute='_compute_qty_at_date_2',
                                             digits='Product Unit of Measure')
    scheduled_date = fields.Datetime(compute='_compute_qty_at_date_2')
    forecast_expected_date = fields.Datetime(compute='_compute_qty_at_date_2')
    free_qty_today = fields.Float(compute='_compute_qty_at_date_2',
                                  digits='Product Unit of Measure')
    qty_available_today = fields.Float(compute='_compute_qty_at_date_2')

    def _get_reserved_qty(self):
        for rec in self:
            rec.qty_reserved = rec.qty_available_today -\
                rec.free_qty_today

    def _compute_qty_available_color(self):
        for rec in self:
            color = 'text-danger'
            if rec.free_qty_today and\
                    rec.qty_to_deliver <= rec.free_qty_today:
                color = 'text-success'
            elif 0 < rec.free_qty_today < rec.qty_to_deliver:
                color = 'text-warning'
            rec.qty_available_color = color

    @api.depends('product_type', 'product_uom_qty', 'qty_delivered', 'state',
                 'move_ids', 'product_uom')
    def _compute_qty_to_deliver(self):
        """Rewrite the Computed visibility of the inventory widget."""
        for line in self:
            line.qty_to_deliver = line.product_uom_qty - line.qty_delivered
            if line.state in ('draft', 'sent', 'sale') and\
                    line.product_type == 'product' and line.product_uom:
                if line.state == 'sale' and not line.move_ids:
                    line.display_qty_widget = False
                else:
                    line.display_qty_widget = True
            else:
                line.display_qty_widget = False

    def _compute_qty_at_date_2(self):
        """ Rewrite the methode _compute_qty_at_date to reuse the simple
        forcasted quantity instead of the forecasted data of the
        related stock.move"""
        treated = self.browse()
        qty_processed_per_product = defaultdict(lambda: 0)
        grouped_lines = defaultdict(lambda: self.env['sale.order.line'])
        # We first loop over the SO lines to group them by warehouse
        # and schedule date in order to batch the read of the quantities
        # computed field.
        for line in self:
            if not (line.product_id and line.display_qty_widget):
                continue
            grouped_lines[(line.warehouse_id.id, line.order_id.commitment_date
                           or line._expected_date())] |= line

        for (warehouse, scheduled_date), lines in grouped_lines.items():
            product_qties = lines.mapped('product_id').with_context(
                warehouse=warehouse).read([
                    'qty_available',
                    'free_qty',
                    'virtual_available',
                ])
            qties_per_product = {
                product['id']: (product['qty_available'], product['free_qty'],
                                product['virtual_available'])
                for product in product_qties
            }
            for line in lines:
                line.scheduled_date = scheduled_date
                (qty_available_today, free_qty_today, virtual_available_at_date
                 ) = qties_per_product[line.product_id.id]
                line.qty_available_today = qty_available_today -\
                    qty_processed_per_product[line.product_id.id]
                line.free_qty_today = free_qty_today -\
                    qty_processed_per_product[line.product_id.id]
                line.virtual_available_at_date = virtual_available_at_date -\
                    qty_processed_per_product[line.product_id.id]
                line.forecast_expected_date = False
                product_qty = line.product_uom_qty
                if line.product_uom and line.product_id.uom_id and line.product_uom != line.product_id.uom_id:
                    line.qty_available_today = line.product_id.uom_id._compute_quantity(line.qty_available_today, line.product_uom)
                    line.free_qty_today = line.product_id.uom_id._compute_quantity(line.free_qty_today, line.product_uom)
                    line.virtual_available_at_date = line.product_id.uom_id._compute_quantity(line.virtual_available_at_date, line.product_uom)
                    product_qty = line.product_uom._compute_quantity(product_qty, line.product_id.uom_id)
                qty_processed_per_product[line.product_id.id] += product_qty
            treated |= lines
        remaining = (self - treated)
        remaining.virtual_available_at_date = False
        remaining.scheduled_date = False
        remaining.forecast_expected_date = False
        remaining.free_qty_today = False
        remaining.qty_available_today = False
