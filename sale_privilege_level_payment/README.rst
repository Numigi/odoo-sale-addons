Sale Privilege Level Payment
============================
This module allows to filter payment acquirers based on privilege levels.

.. contents:: Table of Contents

Configuration
-------------
As ``Website Manager``, I go to the list of payment acquirers.

.. image:: sale_privilege_level_payment/static/description/acquirers_list.png

In the form view of a payment acquirer, I notice a new tab ``Privilege Availability``.

.. image:: sale_privilege_level_payment/static/description/acquirer_form.png

The field ``Privilege Levels`` allows to filter the payment acquirers based on the privilege level.

If one or many privilege levels are selected, the payment acquirer is only selectable for
customers with one of these privilege levels.

If the field is empty, it is selectable by any customer.

Usage
-----
As a customer, I checkout my order.

In the payment step, I see only payment acquirers enabled for my privilege level.

.. image:: sale_privilege_level_payment/static/description/website_shop_payment.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
