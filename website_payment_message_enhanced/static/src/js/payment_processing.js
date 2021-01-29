odoo.define('website_payment_message_enhanced.payment_processing', function (require) {

'use strict';

const PaymentProcessing = require("payment.processing");

PaymentProcessing.include({
    xmlDependencies: PaymentProcessing.prototype.xmlDependencies.concat([
        '/website_payment_message_enhanced/static/src/xml/templates.xml'
    ]),
});

});
