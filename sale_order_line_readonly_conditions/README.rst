Sale Order Line Readonly Conditions
===================================
This module allows to make the fields of a sale order line readonly under a given condition.

The module defines 5 new boolean fields:

* ``handle_widget_invisible``: Makes the handle widget invisible
(see module `web_handle_condition <https://github.com/Numigi/odoo-web-addons/tree/12.0/web_handle_condition>`_).
* ``trash_widget_invisible``: Makes the trash widget invisible
(see module `web_handle_condition <https://github.com/Numigi/odoo-web-addons/tree/12.0/web_handle_condition>`_).
* ``product_readonly``: Makes the product readonly
* ``product_uom_qty_readonly``: Makes the ordered quantity readonly
* ``product_uom_readonly``: Makes the unit of measure readonly
* ``price_unit_readonly``: Makes the unit price readonly
* ``taxes_readonly``: Makes the taxes readonly

However, this module does not define how these flags are checked.
Multiple modules can inherit this module and add their specific use case.

For an example of usage, see the module ``sale_kit`` from the same repository.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
