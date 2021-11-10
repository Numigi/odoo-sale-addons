Website Stock Availability Enhanced
===================================
This module improves the stock availability on the e-commerce application.

.. contents:: Table of Contents

Context
-------
The e-commerce application in vanilla Odoo has limitations regarding the availability of products.

To determine whether a product is available for selling to a customer,
Odoo uses the ``Forecast Quantity`` (a.k.a. the virtual quantity).

This quantity includes products that are expected to be received in the future.

The big issue here is that sometimes, products can take multiple months to be received from the supplier.
It such case, you do not want your customers to expect their orders to be fullfiled soon.

Products
--------
This module adds extra metrics on products.

.. image:: static/description/product_form.png

Quantity Available For Sales
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This metric includes the current stocks in hand, minus the forcasted quantities to deliver.

It does not include any quantity to receive.

Quantity Available Including Next Replenishment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This metric includes the quantity available for sales,
plus the quantity of this product to be received in the next replenishment shipment.

Next Replenishment Delay
~~~~~~~~~~~~~~~~~~~~~~~~
This metric indicates the expected number of days until the next replenishment arrives.

Computation
~~~~~~~~~~~
These metrics are computed distinctly per company.

They are not computed based on the computing mecanisms of Odoo.
They are computed asynchronously based on `Queue Jobs <https://github.com/OCA/queue/tree/12.0>`_.

This prevents the module from significantly impacting the performance of the system.

Write operations on stock moves trigger the recomputation of the metrics for a given product.

Also, a cron job is predefined to execute once per day.
This cron triggers the recomputation of the metrics for all products.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
* Komit (https://komit-consulting.com)

More information
----------------
* Meet us at https://bit.ly/numigi-com
