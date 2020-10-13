Sale Privilege Level Pricelist
==============================
This module allows to set the default pricelist of a customer based on its privilege level.

.. contents:: Table of Contents

Privilege Levels
----------------
In the form view of a privilege level, I notice a new tab ``Pricelists``.

.. image:: static/description/privilege_level_form.png

It contains a mapping indicating which pricelist to use for this privilege level and
a given currency.

Partners
--------
In the form view of a partner, I notice a new field ``Customer Currency``.
This field indicates the currency to use when selling to this partner.

.. image:: static/description/partner_sale_currency.png

I also notice that the ``Sale Pricelist`` is readonly.

.. image:: static/description/partner_pricelist_readonly.png

It is computed based on the partner's privilege level and customer currency.

.. image:: static/description/partner_privilege_level.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
