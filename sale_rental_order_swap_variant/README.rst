Sale Rental Order Swap Variant
==============================
This module allows to change an important component of a kit on a sale order.

Context
-------
By default, when selling a kit, the important components of the kit can not be changed
(the column product is readonly).

With this module, a button on the sale order allows to open a wizard.
This wizard allows to select a different variant (related to the same product template).

Module Name
-----------
This module was first developed in the context of a rental sale order.

However, this module is completely unrelated to the concept of a rental.
This was a conceptual error when initialy developing the module.

A kit can be sold in a normal sale order.
The concept of an important component remains the same.

Configuration
-------------

- I open a type Kit product. In the configuration of the Kit, I have a new option to
   "Change the Variant".
- This option is only available for products which are important.
- I check this option.

.. image:: sale_rental_order_swap_variant/static/description/new_field.png

Use
---

- I create a sale order with a kit product that contains a product for which
   Variant Change is enabled.
- I confirm the SO. A new button appears next to Kit component's product.
   If I click on it, a wizard opens.
- The wizard only allows me to choose another product variant of the same
   product template.

.. image:: sale_rental_order_swap_variant/static/description/new_button_wizard.png

- I confirm the change of Variant in the wizard.
- The article has been changed on my SO line.

.. image:: sale_rental_order_swap_variant/static/description/sol_product_change.png

- If I go to the related pickings (delivery, reception), the article has also been
   changed.

.. image:: sale_rental_order_swap_variant/static/description/delivery_product_change.png

Constraints:

- Product Variant change is not possible if related goods movements have already been
   confirmed.
- If, for example, my Variant Change product has been delivered and I try to change
   the variant, I get the following blocking error message:

.. image:: sale_rental_order_swap_variant/static/description/blocking_error_msg.png

Allow Changing Product
----------------------
It is possible to allow swapping an important component
with a different product (instead of only swapping to a different variant).

.. image:: sale_rental_order_swap_variant/static/description/kit_component_allow_change_product.png

.. image:: sale_rental_order_swap_variant/static/description/kit_component_allow_change_product_2.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
* Komit (https://komit-consulting.com)

More information
----------------
* Meet us at https://bit.ly/numigi-com
