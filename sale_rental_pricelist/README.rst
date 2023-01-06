Sale Rental Pricelist
=====================
This module allows to define distinct pricelists for rental.

.. contents:: Table of Contents

Configuration
-------------

Pricelists
~~~~~~~~~~
I go to the form view of a pricelist.

I notice a new checkbox ``Rental``.

.. image:: sale_rental_pricelist/static/description/pricelist_form.png

Partners
~~~~~~~~
I go to the form view of a commercial partner.

I notice a new field ``Rental Pricelist``.

.. image:: sale_rental_pricelist/static/description/partner_form.png

This field allows to select a pricelist of type ``Rental``.

Usage
-----
I create a new rental order.

.. image:: sale_rental_pricelist/static/description/rental_order_form.png

After selecting my partner, I notice that the rental pricelist was propagated.

..

	This behavior only applies for orders of type ``Rental``.
	On normal sales order, the standard sales pricelist defined on the partner is used.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
