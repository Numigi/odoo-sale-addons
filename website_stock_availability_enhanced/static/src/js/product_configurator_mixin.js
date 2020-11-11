odoo.define('website_stock_availability_enhanced.WebsiteStockAvailabilityEnhanced', function (require) {
'use strict';

var sAnimations = require('website.content.snippets.animation');
var ajax = require('web.ajax');
var core = require('web.core');
var QWeb = core.qweb;

sAnimations.registry.WebsiteSale.include({
     willStart: function () {
         return this._super.apply(this, arguments).then(function () {
             return ajax.loadXML('/website_stock_availability_enhanced/static/src/xml/website_sale_stock_product_availability_enhanced.xml', QWeb);
         })
     },
});

});
