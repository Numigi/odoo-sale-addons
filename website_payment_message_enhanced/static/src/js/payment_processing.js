odoo.define('website_payment_message_enhanced.payment_processing', function (require) {

    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.PaymentProcessing.prototype.xmlDependencies = publicWidget.registry.PaymentProcessing.prototype.xmlDependencies.concat([
        '/website_payment_message_enhanced/static/src/xml/templates.xml'
    ]);

});
