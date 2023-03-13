Sale Partner Authorized Company
===============================
This module allows to restrict the selection of customers on sale order per company.

.. contents:: Table of Contents

Context
-------
In vanilla Odoo, you may prevent users from selling to a given customer.
This feature is not parametrizable per company.

You may also restrict a customer for to be usable only for a single company.
However, you might need to use this customer in different companies
for a purpose other than sales.

Usage
-----
I go to the form view of a partner.

I notice a new field ``Authorized Companies For Sales``.

.. image:: sale_partner_authorized_company/static/description/partner_form.png

I select the company ``Company 1``.
Only this company will therefore be able to sell to this partner.

..

    Letting the field empty means that all companies are allowed
    to sell to this partner.

Connected with ``Company 2``, I create a sale order.

.. image:: sale_partner_authorized_company/static/description/sale_order.png

When selecting my customer, a warning message is displayed.

.. image:: sale_partner_authorized_company/static/description/sale_order_warning.png

Automatically, the partner is unselected from the sale order.

.. image:: sale_partner_authorized_company/static/description/sale_order_partner_empty.png

I must select another customer in order to proceed.

Addresses and Contacts
----------------------
The restriction can only be defined on a commercial partner.

When selecting an address or a contact of a restricted customer,
the same restriction will be applied.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
