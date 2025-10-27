# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import werkzeug
import json
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request


class WebsiteSaleRequestPriceExtended(WebsiteSale):

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'],
                website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        product = request.env['product.product'].browse(int(product_id))

        if product.is_request_price_required:
            return werkzeug.utils.redirect('/shop')

        return super(WebsiteSaleRequestPriceExtended, self).cart_update(
            product_id=product_id, add_qty=add_qty, set_qty=set_qty, **kw)

    @http.route(['/shop/cart/update_json'], type='json', auth="public",
                methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None,
                         display=True):
        product = request.env['product.product'].browse(int(product_id))
        if product.is_request_price_required:
            return {'error': 'This product needs a price request'}

        return super(WebsiteSaleRequestPriceExtended, self).cart_update_json(
            product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty,
            display=display)

    @http.route(['/shop/cart/update_option'], type='http', auth="public",
                methods=['POST'], website=True)
    def cart_options_update_json(self, product_and_options, goto_shop=None, lang=None,
                                 **post):
        product_and_options = json.loads(product_and_options)
        for product_option in product_and_options:
            product_id = product_option.get('product_id')
            if product_id:
                product = request.env['product.product'].browse(int(product_id))
                if product.is_request_price_required:
                    return werkzeug.utils.redirect('/shop')

        return super(WebsiteSaleRequestPriceExtended, self).cart_options_update_json(
            product_and_options=product_and_options, goto_shop=goto_shop, lang=lang,
            **post)

    @http.route('/shop/product/<model("product.template"):product>', type='http',
                auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        """Override to check product access"""
        if product.is_request_price_required:
            pass
        return super(WebsiteSaleRequestPriceExtended, self).product(
            product, category, search, **kwargs)
