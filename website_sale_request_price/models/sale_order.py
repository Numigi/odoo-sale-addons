# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0,
                     **kwargs):
        """
         Override _cart_update to prevent adding products that require price request to cart.

         This method checks both the main product and any product options to ensure
         that products above the price threshold cannot be added to the cart.

         :param product_id: ID of the main product to add/update
         :param line_id: ID of the existing order line to update
         :param add_qty: Quantity to add (can be negative)
         :param set_qty: Quantity to set
         :param kwargs: Additional parameters including product_options
         :raises ValidationError: If any product requires price request
         :return: Result from parent _cart_update method
         """
        if product_id:
            product = self.env['product.product'].browse(product_id)
            if product.is_request_price_required:
                raise ValidationError("This product needs a price request")
        return super(SaleOrder, self)._cart_update(
            product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty,
            **kwargs)
