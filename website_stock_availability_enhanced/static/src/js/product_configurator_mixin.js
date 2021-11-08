odoo.define('website_stock_availability_enhanced.ProductConfiguratorMixin', function (require) {
'use strict';

var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');
var sAnimations = require('website.content.snippets.animation');
var ajax = require('web.ajax');
var core = require('web.core');
var QWeb = core.qweb;
var xml_load = ajax.loadXML(
    '/website_stock_availability_enhanced/static/src/xml/product_availability.xml',
    QWeb
);

ProductConfiguratorMixin._onChangeCombinationStock = function (ev, $parent, combination) {
    if (this.isWebsite && isMainProduct($parent, combination)){
        if (shouldDisableAddToCart(combination)) {
            disableAddToCart($parent)
        }

        xml_load.then(function () {
            updateAvailability(combination)
        })
    }
};

function shouldDisableAddToCart(combination) {
    var qty = $parent.find('input[name="add_qty"]').val();
    return combination.add_to_cart_threshold < qty
}

function disableAddToCart($parent) {
    $parent.find('#add_to_cart').addClass('disabled');
}

function updateAvailability(combination) {
    removeAvailability(combination)
    renderAvailability(combination)
}

function renderAvailability(combination) {
    var $message = $(QWeb.render(
        'website_sale_stock.product_availability',
        combination
    ));
    $('div.availability_messages').html($message);
}

function removeAvailability(combination) {
    const message = $('.oe_website_sale').find('.availability_message_' + combination.product_template)
    message.remove();
}

function isMainProduct($parent, combination) {
    var product_id = 0;
    if ($parent.find('input.product_id:checked').length) {
        product_id = $parent.find('input.product_id:checked').val();
    } else {
        product_id = $parent.find('.product_id').val();
    }
    var isMainProduct = (
        combination.product_id &&
        ($parent.is('.js_main_product') || $parent.is('.main_product')) &&
        combination.product_id === parseInt(product_id)
    );
}

return ProductConfiguratorMixin;

});
