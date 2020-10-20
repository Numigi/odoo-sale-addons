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
        console.log("-------_onClickPriceRequest");
        ev.preventDefault();
        ev.stopPropagation();
        var post = {};
//        $form = $('form[action="/shop/cart/update"]')
//        console.log($form)
//        var productSelector = [
//            'input[type="hidden"][name="product_id"]',
//            'input[type="radio"][name="product_id"]:checked'
//        ];
//        console.log(productSelector)
//        var productReady = this.selectOrCreateProduct(
//            $form,
//            parseInt($form.find(productSelector.join(', ')).first().val(), 10),
//            $form.find('.product_template_id').val(),
//            false
//        );
//        console.log(productReady)
//        var product_id = productReady.done(function (productId) {return productId});
//        console.log(product_id)
//        var post = {
//            "product_id": productId,
//            "quantity": parseFloat($form.find('input[name="add_qty"]').val() || 1),
//        };
//        console.log(post)
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
