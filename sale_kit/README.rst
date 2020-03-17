Sale Kit
========
This module adds kits to sale orders.

.. contents:: Table of Contents

Overview
--------
A product of type ``Kit`` is defined in the module `product_kit <https://github.com/Numigi/odoo-product-addons/tree/12.0/product_kit>`_.

This module defines the behavior on a sale order when a user selects a kit.

.. image:: static/description/overview__sale_order.png

When a kit is selected, a new line is added for each component.

Basic Usage
-----------
I create a new kit with 3 components:

* Two important components
* Two optional components

.. image:: static/description/product_form.png

I create a new sale order.

.. image:: static/description/sale_order_form.png

In a new sale order line, I select my kit.

.. image:: static/description/sale_order_form__kit_product.png

Automatically, 4 new lines are added below the kit.

.. image:: static/description/sale_order_form__kit_components.png

Changing the Kit
----------------
Once a kit is selected on a sale order line, the product can not be changed.

.. image:: static/description/sale_line__kit_readonly.png

However, you may delete the line and recreate it.

.. image:: static/description/sale_line__kit_trash.png

Once deleted, all components for this kit are deleted as well.

.. image:: static/description/sale_line__kit_deleted.png

Components
----------

Important Components
~~~~~~~~~~~~~~~~~~~~
You may not delete an important component:

.. image:: static/description/important_component_trash.png

You may neither change the product, nor the quantity:

.. image:: static/description/important_component_fields.png

You may not move the line:

.. image:: static/description/important_component_handle.png

Non-Important Components
~~~~~~~~~~~~~~~~~~~~~~~~
You may delete a non-important component:

.. image:: static/description/non_important_component_trash.png

You may change its product and quantity:

.. image:: static/description/non_important_component_fields.png

You may move it:

.. image:: static/description/non_important_component_handle.png

You may move the line to another kit:

.. image:: static/description/non_important_component_kit_reference.png

Moving a Kit
~~~~~~~~~~~~
A kit can me moved.

.. image:: static/description/kit_handle.png

When moving a kit, all components are automatically moved as well.

.. image:: static/description/kit_after_reordering.png

Adding a Component
~~~~~~~~~~~~~~~~~~
To add a component to a kit, you have to select the proper ``Kit Reference``.

.. image:: static/description/kit_reference.png

.. image:: static/description/kit_with_new_component.png

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
