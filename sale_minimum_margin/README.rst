Sale Minimum Margin
===================
This module allows to set a minimum sale price margin on product categories.

.. contents:: Table of Contents

Dependencies
------------
It depends on the module `sale_dynamic_price`, which adds prices on products
based on the cost and a margin ratio.

Product Category Configuration
------------------------------
As member of the group `Sales / Manager`, I go to the form view of a product category.

I notice a new field `Minimum Margin Rate`. I set this field to 30%.

.. image:: sale_minimum_margin/static/description/product_category_form.png

When I click on save, the system iterates over all products in the category.

For each product with a margin rate lower than the minimum margin on the category:

.. image:: sale_minimum_margin/static/description/product_before_margin_update.png

(1) The product margin is replaced with the minimum margin.
(2) The product price is recomputed based on the new margin.
(3) A message is logged in the chatter of the product to trace the operation.

.. image:: sale_minimum_margin/static/description/product_after_margin_update.png

Note that products of sub-categories are excluded from this mechanism.
A minimum margin on the category `All / Saleable` does not impact products
of the category `All / Saleable / Parts` for instance.

Constraint On Products
----------------------
As member of the group `Sales / Manager`, I go to the form view of a product.

.. image:: sale_minimum_margin/static/description/product_form.png

I set the margin to a value below the minimum margin.

After filling the new margin, a warning message appears:

.. image:: sale_minimum_margin/static/description/product_lower_margin_warning.png

I am able to bypass this warning and save anyway. Only members of `Sales / Manager` are able to do so.

.. image:: sale_minimum_margin/static/description/product_lower_margin_saved.png

Other users are blocked when clicking on save.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
