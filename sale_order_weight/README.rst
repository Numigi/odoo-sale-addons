Sale Order Weight
=================
This module adds two field to the records of the model Sale Order:
  - weight_in_kg: Weight of the order (kg)
  - weight_in_lb: Weight of the order (lb)

These two fields will be computed every time user create/update sale order line

Computation:
  - If `order_line.product_uom` is not "Unit":

    - `quantity = _compute_quantity(order_line.quantity, unit)`

  - If `order_line.product_uom.category_id` is not "Unit":

    - return `weight_in_kg = weight_in_lb = 0`

  - `weight_in_kg = product.weight * quantity`
  - `weight_in_lb`

    - if `product.specific_weight_uom_id` is "lb":

      - `weight_in_lb = product.weight_in_uom * quantity`

    - else:

      - `weight_in_lb = _compute_quantity(weight_in_kg, lb)`

.. image:: static/description/sale_order_weight.png

Configuration
-------------
No configuration required apart from module installation.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
* Komit (https://komit-consulting.com)

More information
----------------
* Meet us at https://bit.ly/numigi-com
