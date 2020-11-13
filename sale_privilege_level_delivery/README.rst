Sale Privilege Level Delivery
=============================
This module allows to filter available delivery methods on based on privilege levels of the customer.

.. contents:: Table of Contents

Configuration
-------------
As ``Website Manager``, I go to the list of delivery methods.

.. image:: static/description/carriers_list.png

In the form view of a delivery method, I notice a new tab ``Privilege Availability``.

.. image:: static/description/carrier_form.png

The field ``Privilege Levels`` allows to filter the delivery methods based on the privilege level.

If one or many privilege levels are selected, the delivery method is only selectable for
customers with one of these privilege levels.

If the field is empty, it is selectable by any customer.

Sale Orders
-----------
As a member of the group ``Sale / User``, I create a new sale order.

After selecting a customer, I notice that the available delivery methods are
filtered based on the privilege level of this customer.

.. image:: static/description/sale_order.png

E-commerce
----------
As a customer, I checkout my order.

In the payment step, I see only delivery methods enabled for my privilege level.

.. image:: static/description/website_shop_payment.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
