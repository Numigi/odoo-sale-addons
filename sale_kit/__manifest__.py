# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Kit",
    "version": "1.1.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Allow to use kits on sale orders",
    "depends": [
        "base_view_inheritance_extension",
        "product_kit",
        "sale_order_line_readonly_conditions",
    ],
    "data": ["views/assets.xml", "views/sale_order.xml"],
    "installable": True,
}
