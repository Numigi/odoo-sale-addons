Sales Warranty
==============
This module allows to manage warranties on sold products.

.. contents:: Table of Contents

Types of Warranty
-----------------
As member of the group `Warranties / Manager`, you may edit / create new types of warranties.

Go to `Warranties / Configuration / Warranty Types`.

.. image:: sale_warranty/static/description/warranty_type_list.png

Products
--------
As member of the group `Sales / Manager`, you may select warranties on a product.

.. image:: sale_warranty/static/description/product_form.png

Non-serialized Products
~~~~~~~~~~~~~~~~~~~~~~~
By default, warranties are only selectable on products with unique serial numbers.

Non-serialized products can be enabled per warranty type.

.. image:: sale_warranty/static/description/warranty_type_enable_non_serialized.png

In that case, no serial number will be attributed to the warranty when activating it.

Variants
~~~~~~~~
If you use product variants, note that all variants of the same product inherit the same warranty types.

Multi-Company
~~~~~~~~~~~~~
If you have multiple companies, note that each company has its own warranty types.
Therefore, each product has different warranty types per company.

Sale Order
----------
As member of the group `Sales / User`, when you validate a sales order,
warranties are created automatically for each product if required.

.. image:: sale_warranty/static/description/sale_order_validate.png

After validating the order, a smart button `Warranties` appears.
If you click on that button, the warranties related to the sold products appears.

.. image:: sale_warranty/static/description/sale_order_waranty_button.png
.. image:: sale_warranty/static/description/sale_order_waranty_list.png

Each warranty inherits the details from the sale order.

.. image:: sale_warranty/static/description/sale_order_waranty_form.png

Note that some information are not filled on the warranty.

* Serial Number
* Activation Date
* Expiry Date

These 3 fields are only filled on the delivery of the product.

Delivery Order
--------------
As member of the group `Inventory / User`, when validating a delivery order,
the warranties related to the delivered products are activated.

.. image:: sale_warranty/static/description/delivery_order_form_validate.png

.. image:: sale_warranty/static/description/sale_order_waranty_activated.png

* The `Serial Number` selected on the picking is propagated to the warranty.
* The `Activation Date` is set to the current date.
* The `Expiry Date` is set based on the warranty type and the `Activation Date`.

End of Warranty
---------------
A cron job is executed every day to update the status of warranties.

If the current date is greater than the `Warranty End Date` on a warranty, it is changed to `Expired`.

.. image:: sale_warranty/static/description/warranty_form_expired.png

Creating Warranties Manually
----------------------------
As member of the group `Warranties / User`, you may create a warranty manually.

Go to `Warranties / Warranties / Warranties`, then click on `Create`.

Because the warranty is created manually, you must manually fill the serial number, activation date and expiry date.

When all the fields are filled, click on Save.

.. image:: sale_warranty/static/description/warranty_form.png

Then click on the button `Activate`.

.. image:: sale_warranty/static/description/warranty_form_activate_button.png

.. image:: sale_warranty/static/description/warranty_form_activated.png

When the expiry date is reached, the state will be set to `Expired` by the cron.
This is the same behavior as for a warranty generated from a sale order.

Cancelling A Sale Order
-----------------------
When cancelling a sale order, the warranties attached to the order are cancelled.

.. image:: sale_warranty/static/description/sale_order_cancel.png

.. image:: sale_warranty/static/description/sale_order_warranties_cancelled.png

If the sale order is reconfirmed after the cancellation, new warranties are generated.
The warranties previously cancelled are ignored.

Known Issues
------------

Delivering More Products Than Ordered
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If delivering more products than ordered, only a subset of the delivered serial numbers will be attached to a warranty.
No blocking message will alert the user from such anomaly.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
