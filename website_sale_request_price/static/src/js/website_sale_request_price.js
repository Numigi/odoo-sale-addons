odoo.define('website_sale_request_price.request_price', function (require) {
'use strict';

var core = require('web.core');
var sAnimations = require('website.content.snippets.animation');
require('website_sale.website_sale');

sAnimations.registry.WebsiteSaleRequestPrice = sAnimations.Class.extend({
    selector: '.oe_website_sale',
    events: {
        'show.bs.modal': 'async _onClickPriceRequest',
    },
    _onClickPriceRequest: function (ev) {
        ev.stopPropagation();
        var button = $(ev.relatedTarget);
        console.log(button)
        var product_variant = button.data('product');
        var qty = button.data('qty');
        var modal = $(this);
        console.log(modal)
        console.log(modal.find('strong#display_name'))
        modal.find('strong#display_name').text(product_variant.display_name);
        modal.find('input[type="hidden"][name="product_product_id"]').val(product_variant.id);
    },
});

return sAnimations.registry.WebsiteSaleRequestPrice;

});
