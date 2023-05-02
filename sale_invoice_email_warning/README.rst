Sale Invoice Email Warning
==========================

.. contents:: Table of Contents

Context
-------
In vanilla Odoo, when checking out a website order using Stripe as payment method,
there is a server if the invoicing address has no email.

.. image:: static/description/website_error.png

Overview
--------
This module adds a warning on a sale order when the invoiced partner does not have an email.

.. image:: static/description/sale_order_warning.png

This allows to easily find the cause of the error when it happens for a given order. 

Invoicing Email
---------------
The module also adds the email address of the invoicing address on the sale order.

.. image:: static/description/sale_order_invoicing_email.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
