odoo.define('website_sale_request_price.request_price', function (require) {
'use strict';

var sAnimations = require('website.content.snippets.animation');
require('website_sale.website_sale');

sAnimations.registry.WebsiteSaleRequestPrice = sAnimations.Class.extend({
    selector: '.oe_website_sale',
    events: {
        'show.bs.modal #modal_request_price': 'async _onShowModal',
    },
    _onShowModal: function (ev) {
        ev.stopPropagation();
        var button = $(ev.relatedTarget);
        var product_id = button.data('product-id');
        var product_display_name = button.data('product-display-name');
        var form = $('form#modal_request_price_form');
        form.find('#product_display_name').text(product_display_name);
        form.find('input[name="product_product_id"]').val(product_id);
    },
});

return sAnimations.registry.WebsiteSaleRequestPrice;

});
