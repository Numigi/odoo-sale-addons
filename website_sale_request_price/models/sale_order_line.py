# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        """Only block in website context"""
        if vals.get('product_id') and self._context.get('website_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            if product.is_request_price_required:
                raise ValidationError("This product requires a price request.")
        return super(SaleOrderLine, self).create(vals)

    def write(self, vals):
        """Only block in website context"""
        if vals.get('product_id') and self._context.get('website_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            if product.is_request_price_required:
                raise ValidationError("This product requires a price request.")
        return super(SaleOrderLine, self).write(vals)
