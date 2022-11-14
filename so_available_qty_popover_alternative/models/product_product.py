# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models ,_
import logging
logger = logging.getLogger(__name__)

class Product(models.Model):

    _inherit = "product.product"

    def get_warehouse_qty(self, warehouse_id):
        for rec in self:
            total_qty = 0
            main_internal_stock = warehouse_id.lot_stock_id
            child_locations_ids = main_internal_stock.child_ids.filtered(
            lambda loc: loc.usage == "internal")
            for child_id in child_locations_ids :
                child_quants = self.sudo().env['stock.quant'].search(
                    [('product_id', '=', rec.id), ('location_id', '=', child_id.id)])
                for quant in child_quants:
                    total_qty += quant.quantity
            main_quants = self.sudo().env['stock.quant'].search(
                [('product_id', '=', rec.id), ('location_id', '=', main_internal_stock.id)])
            for quant in main_quants:
                total_qty += quant.quantity
            return total_qty


