odoo.define('website_sale_request_price.request_price', function (require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var sAnimations = require('website.content.snippets.animation');
var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');
require('website_sale.website_sale');

sAnimations.registry.WebsiteSaleRequestPrice = sAnimations.Class.extend(ProductConfiguratorMixin, {
    selector: '.oe_website_sale',
    read_events: {
        'click #request_price': 'async _onClickPriceRequest',
    },
    _onClickPriceRequest: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var $form = $(ev.currentTarget).closest("form");
        var productSelector = [
            'input[type="hidden"][name="product_id"]',
            'input[type="radio"][name="product_id"]:checked'
        ];
        var post = {
            "product_product_id": parseInt($form.find(productSelector.join(', ')).first().val(), 10),
            "product_qty": parseFloat($form.find('input[name="add_qty"]').val() || 1),
        };
        return ajax.jsonRpc($('#request_price').attr('action'), 'call', post).then(function (modal) {
            var $modal = $(modal);
            $modal.modal({backdrop: 'static', keyboard: false});
            $modal.find('.modal-body > div').removeClass('container');
            $modal.appendTo('body').modal();
            $modal.on('click', '.js_goto_event', function () {
                $modal.modal('hide');
                $('#confirm_request_price').prop('disabled', false);
            });
        });
    },
});

return sAnimations.registry.WebsiteSaleRequestPrice;

});
