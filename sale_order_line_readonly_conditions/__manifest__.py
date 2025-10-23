# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Order Line Readonly Conditions",
    "version": "14.0.1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Adds predicates to make fields readonly on a sale order line.",
    "depends": [
        "sale",
        "web_trash_condition",
        "web_handle_condition",
        "base_view_inheritance_extension",
    ],
    "data": ["views/sale_order.xml"],
    "installable": True,
}
