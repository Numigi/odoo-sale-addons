odoo.define('website_sale_stock.ProductConfiguratorMixin', function (require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var QWeb = core.qweb;
var xml_load = ajax.loadXML(
    '/website_stock_availability_enhanced/static/src/xml/website_sale_stock_product_availability_enhanced.xml',
    QWeb
);

});
