Sale Inter-Company Service
==========================

Use Case
--------
Suppose you are managing multiple subsidiaries under a parent company.

When selling to a customer, a given subsidiary might not have sufficient inventory to fulfill an order.

When this situation happens, the subsidiary still delivers to the customer, using
the inventory of the parent company.

When doing so, the parent company charges a percent of the sold amount to the subsidiary.

Context
-------
In Odoo, implementing such functionality using inter-company sale and purchase orders
was discarded as an option.

This solution would require too many documents for a simple sale order.

Overview
--------
This module allows to generate a sale order from a company ``X`` on behalf of a company ``Y``.

* The company ``Y`` invoices the final client.
* The company ``X`` invoice the company ``Y``.

A discount in percent is applied to the Interco invoice.
This discount is the profit earned by ``Y`` for concluding the sale.

The inventory operations are entirely done in company ``X``,
therefore, ``Y`` does not even need to have a warehouse defined.

Configuration
-------------
As ``Administrator``, I go to the settings of the ``Sale`` application.

I notice a new section ``Interco Service``.

.. image:: static/description/sale_settings.png

The field ``Discount`` defines the percentage to use for this company when selling on
behalf of another company.

Usage
-----

Create Sale Order
*****************
A sale order is created from ``Company A`` (i.e. the ``Mother`` company).

This order is typed as ``Interco Service``.

.. image:: static/description/sale_order_interco_service.png

On the order, I select ``Company B`` (i.e. the ``Sister`` company) as the company on behalf of which the products are sold.

.. image:: static/description/sale_order_company.png

The remaining fields are the same as for a regular sale order.

Confirm Sale Order
******************
After confirming the sale order, I notice that a delivery order was created.

.. image:: static/description/sale_order_picking.png

The picking was created as if the sale where done from the ``Mother`` company.

.. image:: static/description/picking_form.png

When using this module, it is therefore important to adapt your PDF documents (``Sale Order``, ``Quotation``, and ``Delivery Order``),
so that the company displayed on the header is the ``Sister`` company.

Create Invoices
***************
Back to the sale order, I click to create an invoice.

.. image:: static/description/sale_order_create_invoice.png

A wizard is opened. This wizard is different from the original one.
It is dedicated to the case of invoicing an ``Interco Service``.

When validating, 3 invoices are created.

1. One customer invoice on the ``Mother`` company (for invoicing the ``Sister`` company)
2. One supplier invoice on the ``Sister`` company
3. One customer invoice on the ``Sister`` company (for invoicing the actual customer)

The invoices (1) and (2) are symetrical in both company
and allow to register the intercompany invoicing.

On these 2 invoices, an extra discount is added.
This discount represents the profit earned by the ``Sister`` company for this sale.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
