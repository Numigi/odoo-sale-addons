Payment Auto Confirm Sale Order
===============================
This module allows sale orders from the ecommerce to be confirmed automatically for a given payment method.

.. contents:: Table of Contents

Configuration
-------------
As ``Administrator``, I go to the form view of a payment method.

I notice a new field ``Automatic Order Confirmation``.

.. image:: payment_auto_confirm_sale_order/static/description/payment_acquirer.png

The field has two options:

* Send Quotation
* Confirm Order

Send Quotation
~~~~~~~~~~~~~~
When this option is selected, the quotation is sent to the customer when
checking out an order using this payment method.

..

    This option is useful for payment methods such as Stripe (Credit Cards) or Paypal.
    By default in Odoo, until the transaction is confirmed, the order is left in ``Draft`` state.

    This process can take up to 20 minutes.

    Meanwhile, the shopping cart is not emptied and products can still be added to the same order.
    This behavior causes a mishmash between ordered products and payment transactions.

Confirm Order
~~~~~~~~~~~~~
When this option is selected, the sale order will be confirmed when
checking out an order using this payment method.

A confirmation email is automatically sent to the customer.

Messages
~~~~~~~~
After selecting an option, I adjust the messages for this payment method in regard to this new feature.

.. image:: payment_auto_confirm_sale_order/static/description/payment_acquirer_messages.png

Usage
-----
As a customer, I proceed to checkout.

.. image:: payment_auto_confirm_sale_order/static/description/order_checkout.png

I notice that my order is confirmed.

.. image:: payment_auto_confirm_sale_order/static/description/order_confirmation.png

When I go to the portal view of my order, I notice that it is processing.

.. image:: payment_auto_confirm_sale_order/static/description/portal_order.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
