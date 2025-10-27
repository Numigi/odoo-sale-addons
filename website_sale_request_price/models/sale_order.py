# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0,
                     **kwargs):
        if product_id:
            product = self.env['product.product'].browse(product_id)
            if product.is_request_price_required:
                raise ValidationError("This product needs a price request")
        product_options = kwargs.get('product_options', [])
        for option in product_options:
            option_product_id = option.get('product_id')
            if option_product_id:
                option_product = self.env['product.product'].browse(option_product_id)
                if option_product.is_request_price_required:
                    raise ValidationError(
                        "This product needs a price request")
        return super(SaleOrder, self)._cart_update(
            product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty,
            **kwargs)
