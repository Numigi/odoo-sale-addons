Sales Warranty Extension
========================
This module extends the module sale_warranty. It adds extensions to warranties.

Warranties extensions are managed with sale subscriptions (from Odoo Enterprise).

.. contents:: Table of Contents

Configuration
-------------
As member of the group `Sales / Manager`, I go to `Warranties / Configuration / Warranty Types`.

In the form view of a warranty type, I find a new field `Warranty Extension`.

.. image:: sale_warranty_extension/static/description/warranty_type_form.png

If I check `Warranty Extension`, 2 new fields appear.

.. image:: sale_warranty_extension/static/description/warranty_type_form_with_extension.png

The field `Extension Duration In Months` allows to indicate how many months are added to
the warranty duration.

The field `Related Service Contract` allows to select the subscription template related
to the warranty extension.

Usage
-----
As member of the group `Sales / User`, I create a subscription for my customer.

.. image:: sale_warranty_extension/static/description/subscription_form.png

In the field `Subscription Template`, I select the contract type related to my warranty extension.

I set the subscription stage to `In Progress`.

Then, I go to my sale order and click on `Delivery`.

.. image:: sale_warranty_extension/static/description/sale_order_form_delivery_smart_button.png

I validate the delivery order.

.. image:: sale_warranty_extension/static/description/delivery_order_validate.png

In the form view of the warranty bound to the delivered product, I find a new block of fields `Extension`.

.. image:: sale_warranty_extension/static/description/warranty_form.png

The extension was added because the customer has an active contract with the subscription template
defined on the warranty type. This contract is defined in the field `Related Contract`.

Expiration
----------
When the cron is ran to update the warranties status, if the warranty extension period
is ongoing, the warranty status will not be set to `Expired`.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
