==========================
Sale Product Pack Extended
==========================

This module is an extension of the community module `sale_product_pack <https://github.com/OCA/product-pack/tree/14.0/stock_product_pack>`_ 

It fixe the issue of duplicating a Sale Order.

When I duplicate an SO with a product pack of multiple level of product pack lines, the product pack lines of level 2 are also duplicated.

To solve the issue we override the copy methode, to prevent expanding pack lines while duplicating an SO.


Contributors
~~~~~~~~~~~~
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)